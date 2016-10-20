# ============================================================================
# FILE: default.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.util import error, echo, debug
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
        self.__current_mode = ''
        self.__mode_stack = []
        self.__current_mappings = {}
        self.__input_before = ''
        self.__input_cursor = ''
        self.__input_after = ''

    def start(self, sources, context):
        try:
            # start = time.time()
            context['sources'] = sources
            if 'input' not in context:
                context['input'] = ''
            context['is_redraw'] = False
            self.__default_mappings = self.__vim.eval(
                'g:denite#_default_mappings')
            self.__current_mode = context['mode']

            self.__denite.start(context)
            self.__denite.on_init(context)

            self.init_buffer(context)
            self.__denite.gather_candidates(context)
            self.change_mode(context, self.__current_mode)

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
        self.__vim.command('new denite | resize '
                           + str(context['winheight']))

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

        self.__cursor = 0
        self.__win_cursor = 1

    def update_buffer(self, context):
        prev_len = len(self.__candidates)
        self.__candidates = []
        statusline = '--' + self.__current_mode + '-- '
        for name, all, candidates in self.__denite.filter_candidates(context):
            if len(all) == 0:
                continue
            self.__candidates += candidates
            statusline += '{}({}/{}) '.format(name, len(candidates), len(all))
        if self.__denite.is_async():
            statusline = '[async] ' + statusline
        self.__candidates_len = len(self.__candidates)
        statusline += '%=[{}] {:3}/{:4}'.format(
            context['path'],
            self.__cursor + self.__win_cursor,
            self.__candidates_len)
        self.__window_options['statusline'] = statusline

        del self.__vim.current.buffer[:]
        self.__vim.current.buffer.append(
            [x['word'] for x in
             self.__candidates[self.__cursor:
                               self.__cursor + int(context['winheight'])]])
        del self.__vim.current.buffer[0]

        self.__options['modified'] = False

        if prev_len > self.__candidates_len:
            # Init cursor
            self.__cursor = 0
            self.__win_cursor = 1

        self.move_cursor(context)

    def move_cursor(self, context):
        self.__vim.call('cursor', [self.__win_cursor, 1])
        if context['auto_preview']:
            self.do_action(context, 'preview')

    def change_mode(self, context, mode):
        custom = context['custom']['map']

        self.__current_mode = mode
        self.__current_mappings = self.__default_mappings['_'].copy()
        if '_' in custom:
            self.__current_mappings.update(custom['_'])

        if mode in self.__default_mappings:
            self.__current_mappings.update(self.__default_mappings[mode])
        if mode in custom:
            self.__current_mappings.update(custom[mode])

        self.update_buffer(context)

    def quit_buffer(self, context):
        self.__vim.command('redraw | echo')
        self.__vim.command('bdelete!')
        self.__vim.command('pclose!')

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

    def redraw(self, context):
        context['is_redraw'] = True
        self.__denite.gather_candidates(context)
        self.update_buffer(context)
        context['is_redraw'] = False

    def debug(self, expr):
        debug(self.__vim, expr)

    def error(self, msg):
        self.__vim.call('denite#util#print_error', '[denite]' + str(msg))

    def input_loop(self, context):
        self.__input_before = context.get('input', '')
        self.__input_cursor = ''
        self.__input_after = ''

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

            mapping = self.__current_mappings.get(str(nr), None)
            if not mapping:
                mapping = self.__current_mappings.get(char, None)
            if mapping:
                map_args = re.split(':', mapping)
                arg = ':'.join(map_args[1:])
                if hasattr(self, map_args[0]):
                    func = getattr(self, map_args[0])
                    ret = func(context) if len(map_args) == 1 else func(
                        context, arg)
                    if ret:
                        break
            elif self.__current_mode == 'insert' and not isinstance(
                    nr, str) and nr >= 0x20:
                # Normal input string
                self.__input_before += char
                self.update_input(context)
                continue

            if is_async:
                time.sleep(0.01)
                self.update_buffer(context)

    def quit(self, context):
        self.__denite.on_close(context)
        self.quit_buffer(context)
        self.__result = []
        return True

    def do_action(self, context, action):
        if self.__cursor >= self.__candidates_len:
            return

        candidate = self.__candidates[self.__cursor + self.__win_cursor - 1]
        if 'kind' in candidate:
            kind = candidate['kind']
        else:
            kind = self.__denite.get_sources()[candidate['source']].kind

        prev_id = self.__vim.call('win_getid')
        self.__vim.command('wincmd p')
        is_quit = not self.__denite.do_action(
            context, kind, action, [candidate])
        self.__vim.call('win_gotoid', prev_id)

        if is_quit:
            self.quit_buffer(context)
        self.__result = [candidate]
        return is_quit

    def delete_backward_char(self, context):
        self.__input_before = re.sub('.$', '', self.__input_before)
        self.update_input(context)

    def delete_backward_word(self, context):
        self.__input_before = re.sub('[^/ ]*.$', '', self.__input_before)
        self.update_input(context)

    def delete_backward_line(self, context):
        self.__input_before = ''
        self.update_input(context)

    def paste_from_register(self, context):
        self.__input_before += re.sub(r'\n', '', self.__vim.eval('@"'))
        self.update_input(context)

    def move_to_next_line(self, context):
        if (self.__win_cursor < self.__candidates_len and
                self.__win_cursor < int(context['winheight'])):
            self.__win_cursor += 1
        elif self.__win_cursor + self.__cursor < self.__candidates_len:
            self.__cursor += 1
        self.update_buffer(context)
        self.move_cursor(context)

    def move_to_prev_line(self, context):
        if self.__win_cursor > 1:
            self.__win_cursor -= 1
        elif self.__cursor >= 1:
            self.__cursor -= 1
        self.update_buffer(context)
        self.move_cursor(context)

    def input_command_line(self, context):
        self.__vim.command('redraw')
        input = self.__vim.call(
            'input', context.get('prompt', '# '), context['input'])
        self.__input_before = input
        self.__input_cursor = ''
        self.__input_after = ''
        self.update_input(context)

    def enter_mode(self, context, mode):
        self.__mode_stack.append(self.__current_mode)
        self.change_mode(context, mode)

    def leave_mode(self, context):
        if not self.__mode_stack:
            return self.quit(context)

        self.__current_mode = self.__mode_stack[-1]
        self.__mode_stack = self.__mode_stack[:-1]
        self.change_mode(context, self.__current_mode)
