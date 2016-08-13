# ============================================================================
# FILE: default.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.util import error, echo
from .. import denite

import re
import traceback
import time


class Default(object):

    def __init__(self, vim):
        self.__vim = vim
        self.__denite = denite.Denite(vim)

    def start(self, sources, context):
        try:
            start = time.time()
            context['sources'] = sources
            self.init_buffer(context)
            self.__denite.start()
            candidates = self.__denite.gather_candidates(context)
            self.__vim.current.buffer.append([x['word'] for x in candidates])
            del self.__vim.current.buffer[0]
            del self.__vim.current.buffer[-1]
            self.__options['modified'] = False
            self.error(str(time.time() - start))

            self.input(context)

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
        self.__vim.command('new denite')
        self.__options = self.__vim.current.buffer.options
        del self.__vim.current.buffer[:]
        self.__options['buftype'] = 'nofile'
        self.__options['filetype'] = 'denite'

    def input(self, context):
        prompt_color = context.get('prompt_color', 'Statement')
        prompt = context.get('prompt', '# ')
        cursor_color = context.get('cursor_color', 'Cursor')

        input_before = context.get('input', '')
        input_cursor = ''
        input_after = ''

        esc = self.__vim.eval('"\<Esc>"')
        bs = self.__vim.eval('"\<BS>"')
        ctrlh = self.__vim.eval('"\<C-h>"')

        while True:
            self.__vim.command('redraw')
            echo(self.__vim, prompt_color, prompt)
            echo(self.__vim, 'Normal', input_before)
            echo(self.__vim, cursor_color, input_cursor)
            echo(self.__vim, 'Normal', input_after)

            nr = self.__vim.funcs.getchar(0)
            char = nr if isinstance(nr, str) else chr(nr)
            if nr >= 0x20:
                # Normal input string
                input_before += char
            elif char == esc:
                break
            elif char == bs or char == ctrlh:
                input_before = re.sub('.$', '', input_before)
            else:
                time.sleep(0.1)

    def debug(self, expr):
        denite.util.debug(self.__vim, expr)

    def error(self, msg):
        self.__vim.call('denite#util#print_error', msg)
