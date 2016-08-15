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
        self.__cursor = 0
        self.__win_cursor = 1
        self.__candidates = []
        self.__candidates_len = 0

    def start(self, sources, context):
        try:
            start = time.time()
            context['sources'] = sources
            context['input'] = ''
            context['ignorecase'] = 1
            context['is_async'] = 0
            context['winheight'] = 20
            context['cursor_highlight'] = 'CursorLine'
            self.init_buffer(context)
            self.__denite.start()
            self.__denite.gather_candidates(context)
            self.update_buffer(context)
            self.error(str(time.time() - start))

            self.input(context)

        except Exception:
            for line in traceback.format_exc().splitlines():
                error(self.__vim, line)
            error(self.__vim,
                  'An error has occurred. Please execute :messages command.')

    def init_buffer(self, context):
        self.__vim.command('new denite | resize ' +
                           str(context['winheight']))
        self.__options = self.__vim.current.buffer.options
        self.__options['buftype'] = 'nofile'
        self.__options['filetype'] = 'denite'
        self.cursor_highlight(context)

    def update_buffer(self, context):
        self.__candidates = self.__denite.filter_candidates(context)
        self.__candidates_len = len(self.__candidates)
        del self.__vim.current.buffer[:]
        self.__vim.current.buffer.append(
            [x['word'] for x in
             self.__candidates[self.__cursor:
                               self.__cursor + context['winheight']]])
        del self.__vim.current.buffer[0]
        self.__options['modified'] = False

    def move_to_next_line(self, context):
        if self.__cursor < context['winheight'] - 1:
            self.__cursor += 1
            self.__win_cursor += 1
        self.cursor_highlight(context)

    def move_to_prev_line(self, context):
        if self.__cursor >= 1:
            self.__cursor -= 1
            self.__win_cursor -= 1
        self.cursor_highlight(context)

    def cursor_highlight(self, context):
        self.__vim.command('silent! call matchdelete(10)')
        self.__vim.call('matchaddpos', context['cursor_highlight'],
                        [self.__win_cursor], 10, 10)

    def quit_buffer(self, context):
        self.__vim.command('redraw | echo')
        self.__vim.command('close!')

    def input(self, context):
        prompt_color = context.get('prompt_color', 'Statement')
        prompt = context.get('prompt', '# ')
        cursor_color = context.get('cursor_color', 'Cursor')

        input_before = context.get('input', '')
        input_cursor = ''
        input_after = ''

        esc = self.__vim.eval('"\<Esc>"')
        bs = self.__vim.eval('"\<BS>"')
        cr = self.__vim.eval('"\<CR>"')
        ctrlh = self.__vim.eval('"\<C-h>"')
        ctrln = self.__vim.eval('"\<C-n>"')
        ctrlp = self.__vim.eval('"\<C-p>"')

        while True:
            self.__vim.command('redraw')
            echo(self.__vim, prompt_color, prompt)
            echo(self.__vim, 'Normal', input_before)
            echo(self.__vim, cursor_color, input_cursor)
            echo(self.__vim, 'Normal', input_after)

            nr = self.__vim.funcs.getchar(0) if context[
                'is_async'] else self.__vim.funcs.getchar()
            char = nr if isinstance(nr, str) else chr(nr)
            if not isinstance(nr, str) and nr >= 0x20:
                # Normal input string
                input_before += char
                context['input'] = input_before + input_cursor + input_after
                self.update_buffer(context)
            elif char == esc:
                self.quit_buffer(context)
                break
            elif char == bs or char == ctrlh:
                input_before = re.sub('.$', '', input_before)
                context['input'] = input_before + input_cursor + input_after
                self.update_buffer(context)
            elif char == ctrln:
                self.move_to_next_line(context)
            elif char == ctrlp:
                self.move_to_prev_line(context)
            elif char == cr:
                self.quit_buffer(context)
                self.do_action(context)
                break
            elif context['is_async']:
                time.sleep(0.05)

    def do_action(self, context):
        if self.__cursor < self.__candidates_len:
            self.__vim.call('denite#util#execute_path', 'edit',
                            self.__candidates[self.__cursor]['action__path'])

    def debug(self, expr):
        denite.util.debug(self.__vim, expr)

    def error(self, msg):
        self.__vim.call('denite#util#print_error', msg)
