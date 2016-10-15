# ============================================================================
# FILE: process.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import subprocess
from threading import Thread
from queue import Queue
from time import time
from collections import deque


class Process(object):
    def __init__(self, commands, context, cwd):
        self.__proc = subprocess.Popen(commands,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       cwd=cwd)
        self.__eof = False
        self.__context = context
        self.__thread = Thread(target=self.enqueue_output)
        self.__thread.start()
        self.__queue = Queue()

    def eof(self):
        return self.__eof

    def kill(self):
        if not self.__proc:
            return
        self.__proc.kill()
        self.__proc = None
        self.__queue = None
        self.__thread = None

    def enqueue_output(self):
        for line in self.__proc.stdout:
            self.__queue.put(line.decode(self.__context['encoding'],
                             errors='replace').strip('\n'))

    def communicate(self, timeout):
        if not self.__proc:
            return []

        start = time()
        outs = deque()

        while not self.__queue.empty() and time() < start + timeout:
            outs.append(self.__queue.get_nowait())

        outs = list(outs)

        if self.__thread.is_alive() or not self.__queue.empty():
            return (outs, [])

        _, errs = self.__proc.communicate(timeout=timeout)
        errs = errs.decode(self.__context['encoding'],
                           errors='replace').split('\n')
        self.__eof = True
        self.__proc = None
        self.__thread = None
        self.__queue = None

        return (outs, errs)
