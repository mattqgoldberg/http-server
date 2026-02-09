from server.reader import read_file
from server.mime_types import content_types

error_responses = {
    400: b"HTTP/1.0 400 Bad Request\r\n\r\n",
    404: b"HTTP/1.0 404 Not Found\r\n\r\n",
    501: b"HTTP/1.0 501 Not Implemented\r\n\r\n",
    505: b"HTTP/1.0 505 Version Not Supported\r\n\r\n",
}


def parse_path(target: bytearray):

    if target == b"/":
        return "www/index.html"

    path = target.split(b"?")[0]
    path = path.decode()
    path = "www" + path

    return path

def format_response(file_content: bytes, content_type: str):
    msg = f"HTTP/1.0 200 OK\r\nContent-Length: {len(file_content)}\r\nContent-Type: {content_type}\r\nConnection: close\r\n\r\n".encode("ascii")
    return msg + file_content

def get_content_type(path: str):
    file_ext = path.split(".")[-1]
    if file_ext not in content_types:
        return "text/plain"

    return content_types[file_ext]

def parse_request(headers: bytearray, body: bytearray):

    request_line = headers.split(b"\r\n")[0]
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

    file_content = read_file(path)

    if not file_content:
        return error_responses[404]

    content_type = get_content_type(path)

    formatted_response = format_response(file_content, content_type)

    return formatted_response
