"""TCP HTTP server: accepts connections, buffers request headers, and dispatches to the parser."""

import socket
from enum import Enum
from server.parser import parse_request

HOST = "127.0.0.1"
PORT = 8080
BUFSIZE = 1024
MAX_REQ_SIZE = 8 * 1024


class RequestStatus(Enum):
    """Status of the current request read from the connection."""

    IN_PROGRESS = 1
    COMPLETE = 2
    ABORTED = 3
    TOO_LARGE = 4


def build_request(request: bytearray, data: bytes, conn: socket.socket) -> RequestStatus:
    """Append data to request buffer; when headers are complete, handle and return status."""

    if data == b"":
        return RequestStatus.ABORTED

    request.extend(data)

    if len(request) > MAX_REQ_SIZE:
        if not send_response(conn, b"HTTP/1.1 413 Payload Too Large\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"):
            return RequestStatus.ABORTED
        return RequestStatus.TOO_LARGE

    if b'\r\n\r\n' in request:
        headers, body = request.split(b'\r\n\r\n', 1)
        return handle_request(headers, body, conn)

    return RequestStatus.IN_PROGRESS


def handle_request(headers: bytearray, body: bytearray, conn: socket.socket) -> RequestStatus:
    """Parse the request, send the response, and return COMPLETE or ABORTED."""
    if not send_response(conn, parse_request(headers, body)):
        return RequestStatus.ABORTED

    return RequestStatus.COMPLETE

def send_response(conn: socket.socket, response: bytes) -> bool:
    """Send response bytes on the connection. Return False on send error."""
    try:
        conn.sendall(response)
    except OSError:
        return False
    return True


def handle_connection(s: socket.socket) -> None:
    """Accept one connection and process a single request, then close."""
    conn, addr = s.accept()
    with conn:
        request = bytearray()
        request_status = RequestStatus.IN_PROGRESS
        while request_status == RequestStatus.IN_PROGRESS:
            try:
                data = conn.recv(BUFSIZE)
                request_status = build_request(request, data, conn)
            except OSError:
                request_status = RequestStatus.ABORTED
            if request_status != RequestStatus.IN_PROGRESS:
                break


def main() -> None:
    """Bind to HOST:PORT and accept connections indefinitely."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        while True:
            handle_connection(s)


if __name__ == "__main__":
    main()
