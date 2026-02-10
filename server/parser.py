from server.reader import read_file
from server.mime_types import content_types

error_responses = {
    400: b"HTTP/1.0 400 Bad Request\r\n\r\n",
    404: b"HTTP/1.0 404 Not Found\r\n\r\n",
    501: b"HTTP/1.0 501 Not Implemented\r\n\r\n",
    505: b"HTTP/1.0 505 Version Not Supported\r\n\r\n",
}

hex_digits = b"0123456789abcdefABCDEF"

def has_malformed_percent(path: bytearray) -> bool:

    n = len(path)
    for i in range(n):
        if path[i] == ord('%'):
            if i + 2 >= n:
                return True
            if path[i+1] not in hex_digits or path[i+2] not in hex_digits:
                return True
        
    return False

def parse_path(target: bytearray) -> str | None:

    # Path is everything before first ? (query)
    path,_,_ = target.partition(b"?")

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

    if b"\x00" in path or b"\\" in path:
        return None

    try:
        path_str = path.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return None

    # Post decode checks




    path_str = "www" + path_str

    return path_str

def format_response(file_content: bytes, content_type: str):
    msg = f"HTTP/1.0 200 OK\r\nContent-Length: {len(file_content)}\r\nContent-Type: {content_type}\r\nConnection: close\r\n\r\n".encode("ascii")
    return msg + file_content

def get_content_type(path: str):
    file_ext = path.split(".")[-1]
    if file_ext not in content_types:
        return "text/plain"

    return content_types[file_ext]

def parse_request(headers: bytearray, body: bytearray):

    request_line, _, _ = headers.partition(b"\r\n")
    request_line_tokens = request_line.split()

    if len(request_line_tokens) != 3:
        return error_responses[400]

    method, target, http_version = request_line_tokens

    if method != b"GET":
        return error_responses[501]

    if http_version != b"HTTP/1.0" and http_version != b"HTTP/1.1":
        return error_responses[505]

    path = parse_path(target) 
    print(path)

    if path == None:
        return error_responses[404]

    file_content = read_file(path)

    if file_content == None:
        return error_responses[404]

    content_type = get_content_type(path)

    formatted_response = format_response(file_content, content_type)

    return formatted_response
