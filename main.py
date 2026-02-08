import socket
from enum import Enum

HOST = "127.0.0.1"
PORT = 8080
BUFSIZE = 1024
MAX_REQ_SIZE = 8 * 1024

class RequestStatus(Enum):
    IN_PROGRESS = 1
    COMPLETE = 2
    ABORTED = 3
    TOO_LARGE = 4

# Appends data to request bytearray until end of headers is found
def build_request(request: bytearray, data: bytes, conn: socket.socket):

    if data == b"":
        return RequestStatus.ABORTED

    request.extend(data)

    if len(request) > MAX_REQ_SIZE:
        if not send_response(conn, b"HTTP/1.0 413 Payload Too Large\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"):
            return RequestStatus.ABORTED
        return RequestStatus.TOO_LARGE

    if b'\r\n\r\n' in request:
        headers, body = request.split(b'\r\n\r\n', 1)
        return handle_request(headers, body, conn)

    return RequestStatus.IN_PROGRESS

def handle_request(headers: bytearray, body: bytearray, conn: socket.socket):
    print("Handling request")
    if not send_response(conn, b"HTTP/1.0 200 OK\r\nContent-Length: 6\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\nHello\n"):
        return RequestStatus.ABORTED

    return RequestStatus.COMPLETE

def send_response(conn: socket.socket, response: bytes):
    try:
        conn.sendall(response)
    except Exception as e:
        print(e)
        return False
    return True

def handle_connection(s: socket.socket):
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)

        # Once connected, receive and respond to requests
        request = bytearray()
        request_status = RequestStatus.IN_PROGRESS
        while request_status == RequestStatus.IN_PROGRESS:
            try:
                data = conn.recv(BUFSIZE)
                print("Data recieved")
                request_status = build_request(request, data, conn)
            except:
                request_status = RequestStatus.ABORTED

        print("Request handled:", request_status.name)

    print("Connection closed")



def main():
    print("Starting server")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)

        # Keep listening for new connections indefinitely
        while(True):
            handle_connection(s)


if __name__ == "__main__":
    main()
