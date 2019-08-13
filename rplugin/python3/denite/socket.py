# ============================================================================
# FILE: socket.py
# AUTHOR: Rafael Bodill <justRafi at gmail.com>
# License: MIT license
# ============================================================================

import socket
import typing
from threading import Thread
from queue import Queue
from time import time, sleep

from denite.util import UserContext


class Socket(object):

    def __init__(self, host: str, port: int, commands: typing.List[str],
                 context: UserContext, timeout: int) -> None:
        self._enc = context.get('encoding', 'utf-8')
        self._eof = False
        self._outs: typing.List[str] = []
        self._timeout = timeout
        self._context = context

        self._sock = self.connect(host, port, self._timeout)
        self._welcome = self.receive()
        self.sendall(commands)

        self._queue_out: Queue[str] = Queue()
        self._thread: typing.Optional[Thread] = Thread(
            target=self.enqueue_output)
        self._thread.start()

    @property
    def welcome(self) -> str:
        return self._welcome

    def eof(self) -> bool:
        return self._eof

    def kill(self) -> None:
        if self._sock is not None:
            self._sock.close()

        self._sock = None
        self._queue_out = Queue()
        if self._thread is not None:
            self._thread.join(1.0)
        self._thread = None

    def sendall(self, commands: typing.List[str]) -> None:
        if self._sock is None:
            return
        for command in commands:
            self._sock.sendall(f'{command}\n'.encode(self._enc))

    def receive(self, num: int = 1024) -> str:
        if self._sock is None:
            return ''
        return self._sock.recv(num).decode(self._enc, errors='replace')

    def connect(self, host: str, port: int,
                timeout: int) -> typing.Optional[socket.socket]:
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
        return None

    def enqueue_output(self) -> None:
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

    def communicate(self, timeout: int) -> typing.List[str]:
        if not self._sock or not self._thread:
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
