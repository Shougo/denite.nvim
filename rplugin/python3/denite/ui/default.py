# ============================================================================
# FILE: default.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.util import error
from .. import denite

import traceback


class Default(object):

    def __init__(self, vim):
        self.__vim = vim
        self.__denite = denite.Denite(vim)

    def start(self, context):
        try:
            # start = time.time()
            self.init_buffer(context)
            self.__denite.start()
            candidates = self.__denite.gather_candidates(context)
            self.__vim.current.buffer.append([x['word'] for x in candidates])
            # self.error(str(time.time() - start))
        except Exception:
            for line in traceback.format_exc().splitlines():
                error(self.__vim, line)
            error(self.__vim,
                  'An error has occurred. Please execute :messages command.')
            candidates = []

        self.__vim.vars['denite#_context'] = {
            'candidates': candidates,
        }

    def init_buffer(self, context):
        self.__vim.command('new')
        options = self.__vim.current.buffer.options
        options['buftype'] = 'nofile'

    def debug(self, expr):
        denite.util.debug(self.__vim, expr)

    def error(self, msg):
        self.__vim.call('denite#util#print_error', msg)
