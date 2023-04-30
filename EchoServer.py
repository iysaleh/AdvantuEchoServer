#!/usr/bin/env python3
import socket
import logging

from enum import IntEnum
import time

'''
    EchoServer.py
    Author: Ibraheem Saleh
    Description: A simple Python EchoServer -- it receives data from a client and echoes it back.
                    Main function provided for stand-alone use convenience;
                    EchoServer class can also be imported and used directly in other python applications.
'''

class EchoModeEnum(IntEnum):
    """An enum for the mode of logging to use.

    :description: The log_mode can be one of the following: LOG_CONSOLE, LOG_FILE, LOG_BOTH
                     LOG_CONSOLE: Log to the console.
                     LOG_FILE: Log to a file.
                     LOG_BOTH: Log to both the console and file.

    """
    LOG_CONSOLE = 0
    LOG_FILE  = 1
    LOG_BOTH  = 2

    """Define the string representation of the enum for use in the arg parser. """
    def __str__(self):
        return self.name

class EchoServer:
    """A simple Python EchoServer -- it receives data from a client and echoes it back.

    :param host: The host to bind to.
    :type host: str
    :param port: The port to bind to. (1-65535)
    :type port: int
    :param log_mode: The type of log to use.
    :type log_mode: EchoModeEnum
    :param log_file: The file to log to.
    :param log_file: The file to log to.
    :type log_file: str
    :param log_level: The level of log to use.
    :type log_level: int
    :description: The log_mode can be one of the following: logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL

    """
    def __init__(self, host="localhost", port=7777,log_mode=EchoModeEnum.LOG_BOTH, log_file="EchoServer.log", log_level=logging.DEBUG):
        self.host = host
        self.port = port
        self.log_mode = log_mode
        self.log_file = log_file
        self.log_level = log_level
        if(self.log_mode == EchoModeEnum.LOG_FILE or self.log_mode == EchoModeEnum.LOG_BOTH):
            logging.basicConfig(filename=self.log_file, level=self.log_level,
                                format='%(asctime)s.%(msecs)03d::%(levelname)s::%(name)s::%(message)s',
                                datefmt='%Y-%m-%dT%H:%M:%S')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(0.5) #Needed to support keyboard interrupts
        self.sock.bind((self.host, self.port))

    """Start the server.
        :return None"""
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
            self.log("\nServer closed with KeyboardInterrupt!")
            self.sock.close()
            sys.exit(0)
    """Log a message. See EchoModeEnum for the log modes that are supported.
    :param message: The message to log.
    :param args: Other arguments to log. (similar to print)"""
    def log(self, message, *args):
        if(self.log_mode == EchoModeEnum.LOG_CONSOLE or self.log_mode == EchoModeEnum.LOG_BOTH):
            print(message, *args)
        if(self.log_mode == EchoModeEnum.LOG_FILE or self.log_mode == EchoModeEnum.LOG_BOTH):
            logging.info(message, *args)

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Socket Server")
    parser.add_argument("-s",'--host', action="store", dest="host", required=False, default="localhost")
    parser.add_argument("-p",'--port', action="store", dest="port", type=int, required=False, default=7777)
    parser.add_argument("-m",'--log_mode', action="store", dest="log_mode", type=lambda x: EchoModeEnum[x], required=False, default=EchoModeEnum.LOG_BOTH, choices=list(EchoModeEnum))
    parser.add_argument("-f",'--log_file', action="store", dest="log_file", required=False, default="EchoServer.log")
    parser.add_argument("-l",'--log_level', action="store", dest="log_level", type=lambda x: x.upper(), required=False, default="DEBUG", choices=list(logging._nameToLevel))
    args = parser.parse_args()
    port = args.port
    host = args.host
    log_mode = args.log_mode
    log_file = args.log_file
    log_level = args.log_level
    #Map the logging level enum specified as input to the logging module levels.
    log_level_enum = list(logging._nameToLevel).index(log_level)
    echo_server = EchoServer(host, port, log_mode, log_file, log_level_enum)
    echo_server.serve()
