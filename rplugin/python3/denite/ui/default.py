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
            self.__mappings = self.__vim.eval('g:denite#_default_mappings')

            self.__denite.start()
            self.__denite.on_init(context)

            self.init_buffer(context)
            self.__denite.gather_candidates(context)
            self.update_buffer(context)

            self.error('candidates len = ' + str(self.__candidates_len))
            self.error(str(time.time() - start))
            self.input_loop(context)

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

    def cursor_highlight(self, context):
        self.__vim.command('silent! call matchdelete(10)')
        self.__vim.call('matchaddpos', context['cursor_highlight'],
                        [self.__win_cursor], 10, 10)

    def quit_buffer(self, context):
        self.__vim.command('redraw | echo')
        self.__vim.command('close!')

    def update_input(self, context):
        context['input'] = self.__input_before
        context['input'] += self.__input_cursor
        context['input'] += self.__input_after
        self.update_buffer(context)

    def input_loop(self, context):
        prompt_color = context.get('prompt_color', 'Statement')
        prompt = context.get('prompt', '# ')
        cursor_color = context.get('cursor_color', 'Cursor')

        self.__input_before = context.get('input', '')
        self.__input_cursor = ''
        self.__input_after = ''

        esc = self.__vim.eval('"\<Esc>"')

        while True:
            self.__vim.command('redraw')
            echo(self.__vim, prompt_color, prompt)
            echo(self.__vim, 'Normal', self.__input_before)
            echo(self.__vim, cursor_color, self.__input_cursor)
            echo(self.__vim, 'Normal', self.__input_after)

            nr = self.__vim.funcs.getchar(0) if context[
                'is_async'] else self.__vim.funcs.getchar()
            char = nr if isinstance(nr, str) else chr(nr)
            if not isinstance(nr, str) and nr >= 0x20:
                # Normal input string
                self.__input_before += char
                self.update_input(context)
                continue

            if char in self.__mappings and hasattr(
                    self, self.__mappings[char]):
                func = getattr(self, self.__mappings[char])
                ret = func(context)
                if ret:
                    break
            elif char == esc:
                self.quit_buffer(context)
                break

            if context['is_async']:
                time.sleep(0.05)

    def quit(self, context):
        self.quit_buffer(context)
        return True

    def do_action(self, context):
        if self.__cursor >= self.__candidates_len:
            return

        self.quit_buffer(context)
        self.__denite.do_action(
            context, 'jump_list', 'default',
            [self.__candidates[self.__cursor + self.__win_cursor - 1]])
        return True

    def delete_backward_char(self, context):
        self.__input_before = re.sub('.$', '', self.__input_before)
        self.update_input(context)

    def move_to_next_line(self, context):
        if self.__win_cursor < context['winheight']:
            self.__win_cursor += 1
        elif self.__cursor < self.__candidates_len - 1:
            self.__cursor += 1
        self.update_buffer(context)
        self.cursor_highlight(context)

    def move_to_prev_line(self, context):
        if self.__win_cursor > 1:
            self.__win_cursor -= 1
        elif self.__cursor >= 1:
            self.__cursor -= 1
        self.update_buffer(context)
        self.cursor_highlight(context)

    def input_command_line(self, context):
        self.__vim.command('redraw')
        self.__input_before = self.__vim.call(
            'input', context.get('prompt', '# '), context['input'])
        self.__input_cursor = ''
        self.__input_after = ''
        self.update_input(context)

    def debug(self, expr):
        denite.util.debug(self.__vim, expr)

    def error(self, msg):
        self.__vim.call('denite#util#print_error', msg)
