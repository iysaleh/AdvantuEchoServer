#!/usr/bin/env python3
import socket
import logging

from enum import IntEnum

class EchoLogTypeEnum(IntEnum):
    LOG_CONSOLE = 0
    LOG_FILE  = 1
    LOG_BOTH  = 2

    #Define the string representation of the enum for use in the arg parser.
    def __str__(self):
        return self.name

class EchoServer:
    def __init__(self, host="localhost", port=7777,log_type=EchoLogTypeEnum.LOG_BOTH, log_file="server.log", log_level=logging.DEBUG):
        self.host = host
        self.port = port
        self.log_type = log_type
        self.log_file = log_file
        self.log_level = log_level
        if(self.log_type == EchoLogTypeEnum.LOG_FILE or self.log_type == EchoLogTypeEnum.LOG_BOTH):
            logging.basicConfig(filename=self.log_file, level=self.log_level)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(0.5) #Needed to support keyboard interrupts
        self.sock.bind((self.host, self.port))

    def serve(self):
        self.sock.listen(1)
        self.log("EchoServer Listening on {}:{}".format(self.host, self.port))
        try:
            while True:
                try:
                    client, addr = self.sock.accept()
                    client.settimeout(0.5) #Needed to support keyboard interrupts
                    print("Got connection from", addr)
                    while True:
                        try:
                            data = client.recv(1024)
                            self.log("Client[%s] Echo: %s" % (client.getpeername(),data.decode("utf-8")))
                            if not data:
                                break
                            client.sendall(data)
                        except socket.timeout:
                            pass
                        except KeyboardInterrupt:
                            raise KeyboardInterrupt
                    client.close()
                except socket.timeout:
                    pass
                except KeyboardInterrupt:
                    raise KeyboardInterrupt
        except KeyboardInterrupt:
            self.log("Server closed with KeyboardInterrupt!")
            self.sock.close()
    
    def log(self, message, *args):
        if(self.log_type == EchoLogTypeEnum.LOG_CONSOLE or self.log_type == EchoLogTypeEnum.LOG_BOTH):
            print(message, *args)
        if(self.log_type == EchoLogTypeEnum.LOG_FILE or self.log_type == EchoLogTypeEnum.LOG_BOTH):
            logging.info(message, *args)

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Socket Server")
    parser.add_argument('--host', action="store", dest="host", required=False, default="localhost")
    parser.add_argument('--port', action="store", dest="port", type=int, required=False, default=7777)
    parser.add_argument('--log_type', action="store", dest="log_type", type=lambda x: EchoLogTypeEnum[x], required=False, default=EchoLogTypeEnum.LOG_BOTH, choices=list(EchoLogTypeEnum))
    parser.add_argument('--log_file', action="store", dest="log_file", required=False, default="server.log")
    parser.add_argument('--log_level', action="store", dest="log_level", type=lambda x: getattr(logging, x.upper()), required=False, default=logging.DEBUG, choices=list(logging._nameToLevel))
    args = parser.parse_args()
    port = args.port
    host = args.host
    log_type = args.log_type
    log_file = args.log_file
    log_level = args.log_level
    echo_server = EchoServer(host, port, log_type, log_file, log_level)
    echo_server.serve()
