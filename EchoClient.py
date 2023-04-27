import socket

class EchoClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def send(self, msg):
        self.sock.send(msg.encode())

    def recv(self):
        return self.sock.recv(1024).decode()

    def close(self):
        self.sock.close()

#EchoClient CLI Args (OptionsParser)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='Host', type=str, default='localhost')
    parser.add_argument('--port', help='Port', type=int, default=7777)
    args = parser.parse_args()
    client = EchoClient(args.host, args.port)
    try:
        while True:
            client.send(input())
            print(client.recv())
    except KeyboardInterrupt:
        print("Closing Client - EchoServer Connection.")
        client.close()
    