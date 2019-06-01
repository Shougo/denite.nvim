# ============================================================================
# FILE: parent.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import asyncio
import time
import os
import msgpack
import subprocess
from functools import partial
from pathlib import Path
from queue import Queue

from denite.aprocess import Process
from denite.util import error_tb, error


class _Parent(object):
    def __init__(self, vim):
        self.name = 'parent'

        self._vim = vim

        self._start_process()

    def start(self, context):
        self._put('start', [context])

    def gather_candidates(self, context):
        self._put('gather_candidates', [context])

    def on_init(self, context):
        self._put('on_init', [context])

    def on_close(self, context):
        self._put('on_close', [context])

    def init_syntax(self, context, is_multi):
        self._put('init_syntax', [context, is_multi])

    def filter_candidates(self, context):
        return self._get('filter_candidates', [context])

    def do_action(self, context, action_name, targets):
        return self._get('do_action', [context, action_name, targets])

    def get_action(self, context, action_name, targets):
        return self._get('get_action', [context, action_name, targets])

    def get_action_names(self, context, targets):
        return self._get('get_action_names', [context, targets])


class SyncParent(_Parent):
    def _start_process(self):
        from denite.child import Child
        self._child = Child(self._vim)

    def _put(self, name, args):
        return self._child.main(name, args, queue_id=None)

    def _get(self, name, args, is_async=False):
        return self._put(name, args)


class ASyncParent(_Parent):
    def _start_process(self):
        self._stdin = None
        self._queue_id = ''
        self._queue_in = Queue()
        self._queue_out = Queue()
        self._packer = msgpack.Packer(
            use_bin_type=True,
            encoding='utf-8',
            unicode_errors='surrogateescape')
        self._unpacker = msgpack.Unpacker(
            encoding='utf-8',
            unicode_errors='surrogateescape')

        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        main = str(Path(__file__).parent.parent.parent.parent.joinpath(
            'autoload', 'denite', '_main.py'))

        self._hnd = self._vim.loop.create_task(
            self._vim.loop.subprocess_exec(
                partial(Process, self),
                self._vim.vars.get('python3_host_prog', 'python3'),
                main,
                self._vim.vars['denite#_serveraddr'],
                stderr=None,
                startupinfo=startupinfo))

    def _connect_stdin(self, stdin):
        self._stdin = stdin
        return self._unpacker

    # def filter_candidates(self, context):
    #     if self._queue_id:
    #         # Use previous id
    #         queue_id = self._queue_id
    #     else:
    #         queue_id = self._put('filter_candidates', [context])
    #         if not queue_id:
    #             return (False, [])
    #
    #     get = self._get(queue_id, True)
    #     if not get:
    #         # Skip the next merge_results
    #         self._queue_id = queue_id
    #         return [True, '', [], [], 0]
    #     self._queue_id = ''
    #     results = get[0]
    #     return results if results else [False, '', [], [], 0]

    def _put(self, name, args):
        if not self._hnd:
            return None

        queue_id = str(time.time())
        msg = self._packer.pack({
            'name': name, 'args': args, 'queue_id': queue_id
        })
        self._queue_in.put(msg)

        if self._stdin:
            try:
                while not self._queue_in.empty():
                    self._stdin.write(self._queue_in.get_nowait())
            except BrokenPipeError:
                error_tb(self._vim, 'Crash in child process')
                error(self._vim, 'stderr=' + str(self._proc.read_error()))
                self._hnd = None
        return queue_id

    def _get(self, queue_id, is_async=False):
        if not self._hnd:
            return None

        c = asyncio.sleep(5)
        self._vim.run_coroutine(c)
        return self._vim.vars['denite#_ret']

        # outs = []
        # while not self._queue_out.empty():
        #     outs.append(self._queue_out.get_nowait())
        # try:
        #     return [x for x in outs if x['queue_id'] == queue_id]
        # except TypeError:
        #     error_tb(self._vim,
        #              '"stdout" seems contaminated by sources. '
        #              '"stdout" is used for RPC; Please pipe or discard')
        #     return []
