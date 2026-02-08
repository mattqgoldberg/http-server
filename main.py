import socket

HOST = "127.0.0.1"
PORT = 8080
BUFSIZE = 1024

# Appends data to request bytearray until end of headers is found
def build_request(request: bytearray, data: bytes):

    request.extend(data)

    if b'\r\n\r\n' in request:
        print('Request headers complete')
        print(request)
        return True

    return False

def handle_request(request, conn: socket.socket):
    print("Handling request")
    conn.sendall(b"Hello\n")
    conn.close()

def main():
    print("Starting server")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)

        # Keep connection listen for new connections indefinitely
        while(True):
            conn, addr = s.accept()
            print('Connected by', addr)

            # Once connected, receive and respond to requests
            request = bytearray()
            request_complete = False
            while not request_complete:
                try:
                    data = conn.recv(BUFSIZE)
                    print("Data recieved")
                    request_complete = build_request(request, data)
                except:
                    conn.close()
                    break

            if(request_complete):
                handle_request(request, conn)



if __name__ == "__main__":
    main()
