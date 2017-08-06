# ============================================================================
# FILE: matcher_fzf.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
from denite.util import globruntime, error, convert2fuzzy_pattern
import sys
import os
from subprocess import Popen, PIPE


class Filter(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'matcher_fzf'
        self.description = 'fzf matcher'

        self.__initialized = False
        self.__disabled = False

    def filter(self, context):
        if not context['candidates'] or not context[
                'input'] or self.__disabled:
            return context['candidates']

        if not self.__initialized:
            # fzf installation check
            ext = '.exe' if context['is_windows'] else ''
            if globruntime(context['runtimepath'], 'bin/fzf' + ext):
                # Add path
                sys.path.append(os.path.dirname(
                    globruntime(context['runtimepath'],
                                'bin/fzf' + ext)[0]))
                self.__initialized = True
            else:
                error(self.vim, 'matcher_fzf: bin/fzf' + ext +
                      ' is not found in your runtimepath.')
                error(self.vim, 'matcher_fzf: You must install/build' +
                      ' fzf.')
                self.__disabled = True
                return []

        fzf_result = self._get_fzf_result(context['candidates'],
                                          context['input'],
                                          context['encoding'])
        return [x for x in context['candidates'] if x['word'] in fzf_result]

    def convert_pattern(self, input_str):
        return convert2fuzzy_pattern(input_str)

    def _get_fzf_result(self, candidates, pattern, encoding):
        proc = Popen(['fzf', '+s', '-f', pattern], stdin=PIPE, stdout=PIPE,
                     stderr=PIPE)
        (stdout, stderr) = proc.communicate(
            '\n'.join([d['word'] for d in candidates]).encode(encoding))
        if stderr:
            error(self.vim, 'stderr: ' + '\n'.join(stderr))
        return stdout.decode(encoding)
