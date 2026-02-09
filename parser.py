from reader import read_file

error_responses = {
    400: b"HTTP/1.0 400 Bad Request\r\n\r\n",
    404: b"HTTP/1.0 404 Not Found\r\n\r\n",
    501: b"HTTP/1.0 501 Not Implemented\r\n\r\n",
    505: b"HTTP/1.0 505 Version Not Supported\r\n\r\n",
}

content_types = {
    # HTML & text
    "html": "text/html",
    "htm": "text/html",
    "css": "text/css",
    "js": "application/javascript",
    "txt": "text/plain",
    "csv": "text/csv",
    "json": "application/json",
    "xml": "application/xml",

    # Images
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "bmp": "image/bmp",
    "webp": "image/webp",
    "ico": "image/x-icon",
    "svg": "image/svg+xml",

    # Fonts
    "woff": "font/woff",
    "woff2": "font/woff2",
    "ttf": "font/ttf",
    "otf": "font/otf",
    "eot": "application/vnd.ms-fontobject",

    # Audio
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "ogg": "audio/ogg",

    # Video
    "mp4": "video/mp4",
    "webm": "video/webm",
    "ogv": "video/ogg",

    # Archives
    "zip": "application/zip",
    "tar": "application/x-tar",
    "gz": "application/gzip",
    "rar": "application/vnd.rar",
    "7z": "application/x-7z-compressed",

    # PDFs & misc
    "pdf": "application/pdf",

    # Binary fallback
    "bin": "application/octet-stream",
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
