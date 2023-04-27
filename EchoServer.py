#!/usr/bin/env python3
import socket

class EchoServer:
    def __init__(self, host="localhost", port=7777):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(0.5) #Needed to support keyboard interrupts
        self.sock.bind((self.host, self.port))

    def serve(self):
        self.sock.listen(1)
        print("EchoServer Listening on {}:{}".format(self.host, self.port))
        try:
            while True:
                try:
                    client, addr = self.sock.accept()
                    print("Got connection from", addr)
                    while True:
                        data = client.recv(1024)
                        if not data:
                            break
                        client.sendall(data)
                    client.close()
                except socket.timeout:
                    pass
                except KeyboardInterrupt:
                    raise KeyboardInterrupt
        except KeyboardInterrupt:
            print("Server closed with KeyboardInterrupt!")
            self.sock.close()

#EchoServer CLI Arguments (OptionsParser)

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Socket Server")
    parser.add_argument('--host', action="store", dest="host", required=False, default="localhost")
    parser.add_argument('--port', action="store", dest="port", type=int, required=False, default=7777)
    args = parser.parse_args()
    port = args.port
    host = args.host
    echo_server = EchoServer(host, port)
    echo_server.serve()
