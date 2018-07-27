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


class Process(object):
    def __init__(self, commands, context, cwd):
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        self._proc = subprocess.Popen(commands,
                                      stdin=subprocess.DEVNULL,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      startupinfo=startupinfo,
                                      cwd=cwd)
        self._eof = False
        self._context = context
        self._queue_out = Queue()
        self._thread = Thread(target=self.enqueue_output)
        self._thread.start()

    def eof(self):
        return self._eof

    def kill(self):
        if not self._proc:
            return

        if self._proc.poll() is None:
            # _proc is running
            self._proc.kill()
            self._proc.wait()

        self._proc = None
        self._queue_out = None
        self._thread.join(1.0)
        self._thread = None

    def enqueue_output(self):
        for line in self._proc.stdout:
            if not self._queue_out:
                return
            self._queue_out.put(
                line.decode(self._context['encoding'],
                            errors='replace').strip('\r\n'))

    def communicate(self, timeout):
        if not self._proc:
            return ([], [])

        start = time()
        outs = []

        if self._queue_out.empty():
            sleep(0.1)
        while not self._queue_out.empty() and time() < start + timeout:
            outs.append(self._queue_out.get_nowait())

        if self._thread.is_alive() or not self._queue_out.empty():
            return (outs, [])

        _, errs = self._proc.communicate(timeout=timeout)
        errs = errs.decode(self._context['encoding'],
                           errors='replace').splitlines()
        self._eof = True
        self._proc = None
        self._thread = None
        self._queue = None

        return (outs, errs)
