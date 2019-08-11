# ============================================================================
# FILE: process.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import subprocess
from threading import Thread
from queue import Queue
from time import time, sleep
import os
import typing

from denite.util import UserContext


class Process(object):
    def __init__(self, commands: typing.List[str],
                 context: UserContext, cwd: str) -> None:
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        self._proc: typing.Optional[typing.Any] = subprocess.Popen(
            commands,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo,
            cwd=cwd)
        self._eof = False
        self._context = context
        self._queue_out: Queue[str] = Queue()
        self._thread: typing.Optional[Thread] = Thread(
            target=self.enqueue_output)
        self._thread.start()

    def eof(self) -> bool:
        return self._eof

    def kill(self) -> None:
        if not self._proc:
            return

        if self._proc.poll() is None:
            # _proc is running
            self._proc.kill()
            self._proc.wait()

        self._proc = None
        self._queue_out = Queue()
        if self._thread:
            self._thread.join(1.0)
        self._thread = None

    def enqueue_output(self) -> None:
        if not self._proc:
            return

        for line in self._proc.stdout:
            if not self._thread:
                return
            self._queue_out.put(
                line.decode(self._context['encoding'],
                            errors='replace').strip('\r\n'))

    def communicate(self, timeout: float) -> typing.Tuple[
            typing.List[str], typing.List[str]]:
        if not self._proc:
            return ([], [])

        start = time()
        outs = []

        if self._queue_out.empty():
            sleep(0.1)
        while not self._queue_out.empty() and time() < start + timeout:
            outs.append(self._queue_out.get_nowait())

        if (not self._thread or self._thread.is_alive()
                or not self._queue_out.empty()):
            return (outs, [])

        _, errs = self._proc.communicate(timeout=timeout)
        errs = errs.decode(self._context['encoding'],
                           errors='replace').splitlines()
        self._eof = True
        self._proc = None
        self._thread = None
        self._queue = None

        return (outs, errs)
