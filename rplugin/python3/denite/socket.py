# ============================================================================
# FILE: socket.py
# AUTHOR: Rafael Bodill <justRafi at gmail.com>
# License: MIT license
# ============================================================================

import socket
from threading import Thread
from queue import Queue
from time import time, sleep


class Socket(object):

    def __init__(self, host, port, commands, context, timeout):
        self.__enc = context.get('encoding', 'utf-8')
        self.__eof = False
        self.__outs = []
        self.__timeout = timeout
        self.__context = context

        self.__sock = self.connect(host, port, self.__timeout)
        self.__welcome = self.receive()
        self.sendall(commands)

        self.__queue_out = Queue()
        self.__thread = Thread(target=self.enqueue_output)
        self.__thread.start()

    @property
    def welcome(self):
        return self.__welcome

    def eof(self):
        return self.__eof

    def kill(self):
        if self.__sock is not None:
            self.__sock.close()

        self.__sock = None
        self.__queue_out = None
        self.__thread.join(1.0)
        self.__thread = None

    def sendall(self, commands):
        for command in commands:
            self.__sock.sendall('{}\n'.format(command).encode(self.__enc))

    def receive(self, bytes=1024):
        return self.__sock.recv(bytes).decode(
            self.__enc, errors='replace')

    def connect(self, host, port, timeout):
        for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC,
                                      socket.SOCK_STREAM, socket.IPPROTO_TCP,
                                      socket.AI_ADDRCONFIG):
            family, socket_type, proto, canon_name, sa = res
            sock = None
            try:
                sock = socket.socket(family, socket_type, proto)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                sock.settimeout(timeout)
                sock.connect(sa)
                return sock
            except socket.error as e:
                if sock is not None:
                    sock.close()

                if e is not None:
                    raise e
                else:
                    raise OSError('Socket: getaddrinfo returns an empty list')

    def enqueue_output(self):
        if not self.__queue_out:
            return
        buffer = self.receive(2048)
        buffering = True
        while buffering:
            if '\n' in buffer:
                (line, buffer) = buffer.split('\n', 1)
                self.__queue_out.put(line)
            else:
                more = self.receive()
                if not more:
                    buffering = False
                else:
                    buffer += more

    def communicate(self, timeout):
        if not self.__sock:
            return []

        start = time()
        outs = []

        if self.__queue_out.empty():
            sleep(0.1)
        while not self.__queue_out.empty() and time() < start + timeout:
            outs.append(self.__queue_out.get_nowait())

        if self.__thread.is_alive() or not self.__queue_out.empty():
            return outs

        self.__eof = True
        self.__sock = None
        self.__thread = None
        self.__queue = None

        return outs
