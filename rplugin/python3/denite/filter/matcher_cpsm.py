# ============================================================================
# FILE: matcher_cpsm.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base
from denite.util import globruntime, error, convert2fuzzy_pattern, split_input
import sys
import os


class Filter(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'matcher_cpsm'
        self.description = 'cpsm matcher'

        self.__initialized = False
        self.__disabled = False

    def filter(self, context):
        if not context['candidates'] or not context[
                'input'] or self.__disabled:
            return context['candidates']

        if not self.__initialized:
            # cpsm installation check
            if globruntime(context['runtimepath'], 'bin/cpsm_py.so'):
                # Add path
                sys.path.append(os.path.dirname(
                    globruntime(context['runtimepath'], 'bin/cpsm_py.so')[0]))
                self.__initialized = True
            else:
                error(self.vim, 'matcher_cpsm: bin/cpsm_py.so' +
                      ' is not found in your runtimepath.')
                error(self.vim, 'matcher_cpsm: You must install/build' +
                      ' Python3 support enabled cpsm.')
                self.__disabled = True
                return []

        import cpsm_py
        candidates = context['candidates']
        ispath = (os.path.exists(context['candidates'][0]['word']))
        for pattern in split_input(context['input']):
            cpsm_result = cpsm_py.ctrlp_match(
                (d['word'] for d in candidates),
                pattern, limit=1000, ispath=ispath)[0]
            candidates = [x for x in candidates if x['word'] in cpsm_result]
        return candidates

    def convert_pattern(self, input_str):
        return convert2fuzzy_pattern(input_str)
