# ============================================================================
# FILE: grep.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import shlex

from denite import util, process
from os.path import relpath

from .base import Base


GREP_HEADER_SYNTAX = (
    'syntax match deniteSource_grepHeader '
    r'/\v[^:]*:\d+(:\d+)? / '
    'contained keepend')

GREP_FILE_SYNTAX = (
    'syntax match deniteSource_grepFile '
    r'/[^:]*:/ '
    'contained containedin=deniteSource_grepHeader '
    'nextgroup=deniteSource_grepLineNR')
GREP_FILE_HIGHLIGHT = 'highlight default link deniteSource_grepFile Comment'

GREP_LINE_SYNTAX = (
    'syntax match deniteSource_grepLineNR '
    r'/\d\+\(:\d\+\)\?/ '
    'contained containedin=deniteSource_grepHeader')
GREP_LINE_HIGHLIGHT = 'highlight default link deniteSource_grepLineNR LineNR'

GREP_PATTERNS_HIGHLIGHT = 'highlight default link deniteGrepPatterns Function'


def _candidate(result, path):
    return {
        'word': result[3],
        'abbr': '{0}:{1}{2} {3}'.format(
            path,
            result[1],
            (':' + result[2] if result[2] != '0' else ''),
            result[3]),
        'action__path': result[0],
        'action__line': result[1],
        'action__col': result[2],
        'action__text': result[3],
    }


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'grep'
        self.kind = 'file'
        self.vars = {
            'command': ['grep'],
            'default_opts': ['-inH'],
            'recursive_opts': ['-r'],
            'pattern_opt': ['-e'],
            'separator': ['--'],
            'final_opts': ['.'],
            'min_interactive_pattern': 3,
        }
        self.matchers = ['matcher_ignore_globs', 'matcher_regexp']

    def on_init(self, context):
        context['__proc'] = None

        # Backwards compatibility for `ack`
        if (self.vars['command'] and
                self.vars['command'][0] == 'ack' and
                self.vars['pattern_opt'] == ['-e']):
            self.vars['pattern_opt'] = ['--match']

        args = dict(enumerate(context['args']))

        # paths
        arg = args.get(0, [])
        if arg:
            if isinstance(arg, str):
                arg = [arg]
            elif not isinstance(arg, list):
                raise AttributeError('`args[0]` needs to be a `str` or `list`')
        else:
            arg = [context['path']]
        context['__paths'] = [util.abspath(self.vim, x) for x in arg]

        # arguments
        arg = args.get(1, [])
        if arg:
            if isinstance(arg, str):
                arg = shlex.split(arg)
            elif not isinstance(arg, list):
                raise AttributeError('`args[1]` needs to be a `str` or `list`')
        context['__arguments'] = arg

        # patterns
        arg = args.get(2, [])
        if arg:
            if isinstance(arg, str):
                if arg == '!':
                    # Interactive mode
                    context['is_interactive'] = True
                    arg = ''
                else:
                    arg = [arg]
            elif not isinstance(arg, list):
                raise AttributeError('`args[2]` needs to be a `str` or `list`')
        elif context['input']:
            arg = [context['input']]
        else:
            pattern = util.input(self.vim, context, 'Pattern: ')
            if pattern:
                arg = [pattern]
        context['__patterns'] = arg

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
        self.vim.command(GREP_PATTERNS_HIGHLIGHT)

    def define_syntax(self):
        self.vim.command(
            'syntax region ' + self.syntax_name + ' start=// end=/$/ '
            'contains=deniteSource_grepHeader,deniteMatchedRange contained')
        self.vim.command(
            'syntax match deniteGrepPatterns ' +
            r'/%s/ ' % r'\|'.join(util.regex_convert_str_vim(pattern)
                                  for pattern in self.context['__patterns']) +
            'contained containedin=' + self.syntax_name)

    def gather_candidates(self, context):
        if context['event'] == 'interactive':
            # Update input
            self.on_close(context)

            if (not context['input'] or
                    len(context['input']) <
                    self.vars['min_interactive_pattern']):
                return []

            context['__patterns'] = [
                '.*'.join(util.split_input(context['input']))]

        if context['__proc']:
            if not context['is_redraw']:
                return self.__async_gather_candidates(
                    context, context['async_timeout'])
            self.on_close(context)

        if not context['__patterns'] or not self.vars['command']:
            return []

        args = [util.expand(self.vars['command'][0])]
        args += self.vars['command'][1:]
        args += self.vars['default_opts']
        args += self.vars['recursive_opts']
        args += context['__arguments']
        for pattern in context['__patterns']:
            args += self.vars['pattern_opt'] + [pattern]
        args += self.vars['separator']
        if context['__paths']:
            args += context['__paths']
        else:
            args += self.vars['final_opts']

        self.print_message(context, args)

        context['__proc'] = process.Process(args, context, context['path'])
        return self.__async_gather_candidates(context, 0.5)

    def __async_gather_candidates(self, context, timeout):
        outs, errs = context['__proc'].communicate(timeout=timeout)
        if errs:
            self.error_message(errs)
        context['is_async'] = not context['__proc'].eof()
        if context['__proc'].eof():
            context['__proc'] = None

        candidates = []

        for line in outs:
            result = util.parse_jump_line(context['path'], line)
            if not result:
                continue
            path = relpath(result[0], start=context['path'])
            candidates.append(_candidate(result, path))
        return candidates
