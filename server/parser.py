"""HTTP request parsing and response formatting."""

from server.reader import read_file
from server.mime_types import content_types

error_responses = {
    400: b"HTTP/1.1 400 Bad Request\r\n\r\n",
    404: b"HTTP/1.1 404 Not Found\r\n\r\n",
    501: b"HTTP/1.1 501 Not Implemented\r\n\r\n",
    505: b"HTTP/1.1 505 Version Not Supported\r\n\r\n",
}

hex_digits = b"0123456789abcdefABCDEF"


def has_host_header(headers: bytes) -> bool:
    """Return True if the header block contains a Host header (case-insensitive)."""
    lines = headers.split(b"\r\n")
    # First line is request line; rest are header lines
    for line in lines[1:]:
        if line.strip().lower().startswith(b"host:"):
            return True
    return False


def has_malformed_percent(path: bytearray) -> bool:
    """Return True if path contains a malformed %-encoding (e.g. % without two hex digits)."""
    n = len(path)
    for i in range(n):
        if path[i] == ord('%'):
            if i + 2 >= n:
                return True
            if path[i+1] not in hex_digits or path[i+2] not in hex_digits:
                return True
        
    return False


def percent_decode(path_str: str) -> str:
    """Decode %XX sequences to characters. Caller must have validated with has_malformed_percent."""
    result = []
    i = 0
    while i < len(path_str):
        if path_str[i] == "%" and i + 2 < len(path_str):
            hex_pair = path_str[i + 1 : i + 3]
            result.append(chr(int(hex_pair, 16)))
            i += 3
        else:
            result.append(path_str[i])
            i += 1
    return "".join(result)


def parse_path(target: bytearray) -> str | None:
    """
    Parse request-target into a filesystem path under www/, or None if invalid.
    Rejects directory traversal, malformed percent-encoding, and non-UTF-8 paths.
    """
    path, _, _ = target.partition(b"?")

    if len(path) == 0:
        return None

    # Default / becomes index.html
    if path == b"/":
        return "www/index.html"

    if has_malformed_percent(path):
        return None

    # single backslash is wrong, only allow forward slash
    if b"\\" in path:
        return None

    # path must start with /
    if path[0] != ord('/'):
        return None

    if b"\x00" in path:
        return None

    try:
        path_str = path.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return None

    # Post decode checks
    decoded_path = percent_decode(path_str)
    segments = [s for s in decoded_path.split("/") if s]
    if ".." in segments:
        return None

    path_str = "www" + path_str

    return path_str


def format_response(file_content: bytes, content_type: str) -> bytes:
    """Build an HTTP/1.1 200 response with Content-Length and Content-Type headers."""
    msg = f"HTTP/1.1 200 OK\r\nContent-Length: {len(file_content)}\r\nContent-Type: {content_type}\r\nConnection: close\r\n\r\n".encode("ascii")
    return msg + file_content


def get_content_type(path: str) -> str:
    """Return the Content-Type for a path based on its file extension."""
    file_ext = path.split(".")[-1]
    if file_ext not in content_types:
        return "text/plain"

    return content_types[file_ext]


def parse_request(headers: bytearray, body: bytearray) -> bytes:
    """
    Parse an HTTP request and return the response bytes.
    Accepts GET only; requires Host for HTTP/1.1. Returns error response bytes on failure.
    """
    request_line, _, _ = headers.partition(b"\r\n")
    request_line_tokens = request_line.split()

    if len(request_line_tokens) != 3:
        return error_responses[400]

    method, target, http_version = request_line_tokens

    if method != b"GET":
        return error_responses[501]

    if http_version != b"HTTP/1.0" and http_version != b"HTTP/1.1":
        return error_responses[505]

    if http_version == b"HTTP/1.1" and not has_host_header(bytes(headers)):
        return error_responses[400]

    path = parse_path(target)

    if path is None:
        return error_responses[404]

    file_content = read_file(path)

    if file_content is None:
        return error_responses[404]

    content_type = get_content_type(path)

    formatted_response = format_response(file_content, content_type)

    return formatted_response
