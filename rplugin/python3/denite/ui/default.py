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
        self.__result = []
        self.__mode = '_'

    def start(self, sources, context):
        try:
            # start = time.time()
            context['sources'] = sources
            if 'input' not in context:
                context['input'] = ''
            context['ignorecase'] = 1
            context['path'] = ''
            context['winheight'] = 20
            self.__mappings = self.__vim.eval(
                'g:denite#_default_mappings')['_'].copy()
            self.__mappings.update(context['custom']['map']['_'])
            # debug(self.__vim, self.__mappings)

            self.__denite.start(context)
            self.__denite.on_init(context)

            self.init_buffer(context)
            self.__denite.gather_candidates(context)
            self.update_buffer(context)

            # self.error('candidates len = ' + str(self.__candidates_len))
            # self.error(str(time.time() - start))
            self.input_loop(context)

        except Exception:
            for line in traceback.format_exc().splitlines():
                error(self.__vim, line)
            error(self.__vim,
                  'An error has occurred. Please execute :messages command.')
        return self.__result

    def init_buffer(self, context):
        self.__vim.command('new denite | resize ' +
                           str(context['winheight']))

        self.__options = self.__vim.current.buffer.options
        self.__options['buftype'] = 'nofile'
        self.__options['filetype'] = 'denite'
        self.__options['swapfile'] = False

        self.__window_options = self.__vim.current.window.options
        self.__window_options['cursorline'] = True
        self.__window_options['colorcolumn'] = ''
        self.__window_options['number'] = False
        self.__window_options['foldenable'] = False
        self.__window_options['foldcolumn'] = 0

        self.cursor_highlight(context)

    def update_buffer(self, context):
        prev_len = len(self.__candidates)
        self.__candidates = []
        statusline = ''
        if self.__denite.is_async():
            statusline += '[async]'
        for name, all, candidates in self.__denite.filter_candidates(context):
            if len(all) == 0:
                continue
            self.__candidates += candidates
            statusline += '{}({}/{}) '.format(name, len(candidates), len(all))
        self.__candidates_len = len(self.__candidates)
        statusline += '%=[{}] {:3}/{:4}'.format(
            context['directory'],
            self.__cursor + self.__win_cursor,
            self.__candidates_len)
        self.__window_options['statusline'] = statusline


        del self.__vim.current.buffer[:]
        self.__vim.current.buffer.append(
            [x['word'] for x in
             self.__candidates[self.__cursor:
                               self.__cursor + context['winheight']]])
        del self.__vim.current.buffer[0]

        self.__options['modified'] = False

        if prev_len > self.__candidates_len:
            # Init cursor
            self.__cursor = 0
            self.__win_cursor = 1

    def cursor_highlight(self, context):
        self.__vim.call('cursor', [self.__win_cursor, 1])

    def quit_buffer(self, context):
        self.__vim.command('redraw | echo')
        self.__vim.command('bdelete!')

    def update_prompt(self, context):
        prompt_color = context.get('prompt_color', 'Statement')
        prompt = context.get('prompt', '# ')
        cursor_color = context.get('cursor_color', 'Cursor')

        self.__vim.command('redraw')
        echo(self.__vim, prompt_color, prompt)
        echo(self.__vim, 'Normal', self.__input_before)
        echo(self.__vim, cursor_color, self.__input_cursor)
        echo(self.__vim, 'Normal', self.__input_after)

    def update_input(self, context):
        context['input'] = self.__input_before
        context['input'] += self.__input_cursor
        context['input'] += self.__input_after
        self.update_buffer(context)
        self.update_prompt(context)
        self.__win_cursor = 1

    def input_loop(self, context):
        self.__input_before = context.get('input', '')
        self.__input_cursor = ''
        self.__input_after = ''

        esc = self.__vim.eval('"\<Esc>"')

        while True:
            self.update_prompt(context)

            is_async = self.__denite.is_async()
            try:
                if is_async:
                    nr = self.__vim.call('denite#util#getchar', 0)
                else:
                    nr = self.__vim.call('denite#util#getchar')
            except:
                self.quit(context)
                break

            char = nr if isinstance(nr, str) else chr(nr)
            if not isinstance(nr, str) and nr >= 0x20:
                # Normal input string
                self.__input_before += char
                self.update_input(context)
                continue

            if str(nr) in self.__mappings and hasattr(
                    self, self.__mappings[str(nr)]):
                func = getattr(self, self.__mappings[str(nr)])
                ret = func(context)
                if ret:
                    break
            elif char == esc:
                self.quit(context)
                break

            if is_async:
                time.sleep(0.05)
                self.update_buffer(context)

    def quit(self, context):
        self.__denite.on_close(context)
        self.quit_buffer(context)
        self.__result = []
        return True

    def do_action(self, context):
        if self.__cursor >= self.__candidates_len:
            return

        self.quit_buffer(context)
        candidate = self.__candidates[self.__cursor + self.__win_cursor - 1]
        if 'kind' in candidate:
            kind = candidate['kind']
        else:
            kind = self.__denite.get_sources()[candidate['source']].kind
        self.__denite.do_action(context, kind, 'default', [candidate])
        self.__result = [candidate]
        return True

    def delete_backward_char(self, context):
        self.__input_before = re.sub('.$', '', self.__input_before)
        self.update_input(context)

    def delete_backward_word(self, context):
        self.__input_before = re.sub('[^/ ]*.$', '', self.__input_before)
        self.update_input(context)

    def delete_backward_line(self, context):
        self.__input_before = ''
        self.update_input(context)

    def paste_from_unnamed_register(self, context):
        self.__input_before += re.sub(r'\n', '', self.__vim.eval('@"'))
        self.update_input(context)

    def move_to_next_line(self, context):
        if (self.__win_cursor < self.__candidates_len and
                self.__win_cursor < context['winheight']):
            self.__win_cursor += 1
        elif self.__win_cursor + self.__cursor < self.__candidates_len:
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
        input = self.__vim.call(
            'input', context.get('prompt', '# '), context['input'])
        self.__input_before = input
        self.__input_cursor = ''
        self.__input_after = ''
        self.update_input(context)

    def error(self, msg):
        self.__vim.call('denite#util#print_error', '[denite]' + str(msg))
