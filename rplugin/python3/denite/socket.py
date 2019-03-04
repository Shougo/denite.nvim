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
        self._enc = context.get('encoding', 'utf-8')
        self._eof = False
        self._outs = []
        self._timeout = timeout
        self._context = context

        self._sock = self.connect(host, port, self._timeout)
        self._welcome = self.receive()
        self.sendall(commands)

        self._queue_out = Queue()
        self._thread = Thread(target=self.enqueue_output)
        self._thread.start()

    @property
    def welcome(self):
        return self._welcome

    def eof(self):
        return self._eof

    def kill(self):
        if self._sock is not None:
            self._sock.close()

        self._sock = None
        self._queue_out = None
        self._thread.join(1.0)
        self._thread = None

    def sendall(self, commands):
        for command in commands:
            self._sock.sendall(f'{command}\n'.encode(self._enc))

    def receive(self, bytes=1024):
        return self._sock.recv(bytes).decode(
            self._enc, errors='replace')

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
        if not self._queue_out:
            return
        buffer = self.receive(2048)
        buffering = True
        while buffering:
            if '\n' in buffer:
                (line, buffer) = buffer.split('\n', 1)
                self._queue_out.put(line)
            else:
                more = self.receive()
                if not more:
                    buffering = False
                else:
                    buffer += more

    def communicate(self, timeout):
        if not self._sock:
            return []

        start = time()
        outs = []

        if self._queue_out.empty():
            sleep(0.1)
        while not self._queue_out.empty() and time() < start + timeout:
            outs.append(self._queue_out.get_nowait())

        if self._thread.is_alive() or not self._queue_out.empty():
            return outs

        self._eof = True
        self._sock = None
        self._thread = None
        self._queue = None

        return outs
