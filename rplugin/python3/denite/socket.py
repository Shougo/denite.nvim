# ============================================================================
# FILE: socket.py
# AUTHOR: Rafael Bodill <justRafi at gmail.com>
# License: MIT license
# ============================================================================

import socket
from threading import Thread
from queue import Queue
from time import time, sleep
from collections import deque


class Socket(object):

    def __init__(self, host, port, command, context, timeout):
        self.__enc = context.get('encoding', 'utf-8')
        self.__eof = False
        self.__outs = []
        self.__timeout = timeout
        self.__context = context

        self.__sock = self.connect(host, port, self.__timeout)
        self.__welcome = self.__sock.recv(1024).decode(self.__enc)
        self.__sock.sendall('{}\n'.format(command).encode(self.__enc))

        self.__queue_out = Queue()
        self.__thread = Thread(target=self.enqueue_output)
        self.__thread.start()

    @property
    def welcome(self):
        return self.__welcome

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
                    raise ConnectionError(
                        'Socket: getaddrinfo returns an empty list')

    def enqueue_output(self):
        if not self.__queue_out:
            return
        buffer = self.__sock.recv(2048).decode(self.__enc, errors='replace')
        buffering = True
        while buffering:
            if buffer.strip() == 'OK':
                buffering = False
            elif '\n' in buffer:
                (line, buffer) = buffer.split('\n', 1)
                self.__queue_out.put(line)
            else:
                more = self.__sock.recv(1024) \
                        .decode(self.__enc, errors='replace')
                if not more:
                    buffering = False
                else:
                    buffer += more

    def eof(self):
        return self.__eof

    def kill(self):
        if self.__sock is not None:
            self.__sock.close()

        self.__sock = None
        self.__queue_out = None
        self.__thread = None
        self.__outs = None

    def communicate(self, timeout):
        if not self.__sock:
            return []

        start = time()
        outs = deque()

        while not self.__queue_out.empty() and time() < start + timeout:
            outs.append(self.__queue_out.get_nowait())

        outs = list(outs)
        if self.__outs:
            outs = self.__outs + outs
            self.__outs = None

        sleep(0.1)
        if self.__thread.is_alive() or not self.__queue_out.empty():
            if len(outs) < 5000:
                # Skip the update
                self.__outs = outs
                return []
            return outs

        self.__eof = True
        self.__sock = None
        self.__thread = None
        self.__queue = None
        return outs
