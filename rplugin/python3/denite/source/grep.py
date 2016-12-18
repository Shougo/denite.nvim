# ============================================================================
# FILE: grep.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
from denite.util import parse_jump_line, escape_syntax
from denite.process import Process
import os
import shlex

GREP_HEADER_SYNTAX = '''
syntax match deniteSource_grepHeader /\\v[^:]*:\d+(:\d+)? / contained keepend
'''.strip()

GREP_FILE_SYNTAX = (
    'syntax match deniteSource_grepFile '
    '/[^:]*:/ contained '
    'containedin=deniteSource_grepHeader '
    'nextgroup=deniteSource_grepLineNR')
GREP_FILE_HIGHLIGHT = 'highlight default link deniteSource_grepFile Comment'

GREP_LINE_SYNTAX = (
    'syntax match deniteSource_grepLineNR '
    '/\d\+\(:\d\+\)\?/ '
    'contained containedin=deniteSource_grepHeader')
GREP_LINE_HIGHLIGHT = 'highlight default link deniteSource_grepLineNR LineNR'


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'grep'
        self.kind = 'file'
        self.vars = {
            'command': ['grep'],
            'default_opts': ['-inH'],
            'recursive_opts': ['-r'],
            'separator': ['--'],
            'final_opts': ['.'],
        }
        self.matchers = ['matcher_ignore_globs', 'matcher_regexp']

    def on_init(self, context):
        context['__proc'] = None
        directory = ''
        if context['args']:
            directory = context['args'][0]
        if not directory:
            directory = context['path']
        context['__arguments'] = context['args'][1:]
        context['__directory'] = self.vim.call('expand', directory)
        context['__input'] = context['input']
        if not context['__input']:
            context['__input'] = self.vim.call('input', 'Pattern: ')

    def on_close(self, context):
        if context['__proc']:
            context['__proc'].kill()
            context['__proc'] = None

    def highlight(self):
        self.vim.command(GREP_HEADER_SYNTAX)
        self.vim.command(GREP_FILE_SYNTAX)
        self.vim.command(GREP_FILE_HIGHLIGHT)
        self.vim.command(GREP_LINE_SYNTAX)
        self.vim.command(GREP_LINE_HIGHLIGHT)
        self.vim.command('highlight default link deniteGrepInput Function')

    def define_syntax(self):
        input_str = self.context['__input']
        self.vim.command(
            'syntax region ' + self.syntax_name + ' start=// end=/$/ '
            'contains=deniteSource_grepHeader,deniteMatched contained')
        self.vim.command(
            'syntax match deniteGrepInput /%s/ ' % escape_syntax(input_str) +
            'contained containedin=' + self.syntax_name)

    def gather_candidates(self, context):
        if context['__proc']:
            return self.__async_gather_candidates(context, 0.5)

        if context['__input'] == '':
            return []

        commands = []
        commands += self.vars['command']
        commands += self.vars['default_opts']
        commands += self.vars['recursive_opts']
        commands += context['__arguments']
        commands += self.vars['separator']
        commands += shlex.split(context['__input'])
        commands += self.vars['final_opts']
        if context['is_windows']:
            # Windows needs to specify the directory.
            commands += context['__directory']

        context['__proc'] = Process(commands, context, context['__directory'])
        return self.__async_gather_candidates(context, 2.0)

    def __async_gather_candidates(self, context, timeout):
        outs, errs = context['__proc'].communicate(timeout=timeout)
        context['is_async'] = not context['__proc'].eof()
        if context['__proc'].eof():
            context['__proc'] = None

        candidates = []

        for line in outs:
            result = parse_jump_line(context['__directory'], line)
            if result:
                candidates.append({
                    'word': '{0}:{1}{2} {3}'.format(
                        os.path.relpath(result[0],
                                        start=context['__directory']),
                        result[1],
                        (':' + result[2] if result[2] != '0' else ''),
                        result[3]),
                    'action__path': result[0],
                    'action__line': result[1],
                    'action__col': result[2],
                })
        return candidates
