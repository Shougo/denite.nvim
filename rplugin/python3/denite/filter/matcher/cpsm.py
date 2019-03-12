# ============================================================================
# FILE: matcher/cpsm.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import sys
import os

from denite.base.filter import Base
from denite.util import globruntime, convert2fuzzy_pattern


class Filter(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'matcher/cpsm'
        self.description = 'cpsm matcher'

        self._initialized = False
        self._disabled = False

    def filter(self, context):
        if not context['candidates'] or not context[
                'input'] or self._disabled:
            return context['candidates']

        if not self._initialized:
            # cpsm installation check
            ext = '.pyd' if context['is_windows'] else '.so'
            if globruntime(context['runtimepath'], 'bin/cpsm_py' + ext):
                # Add path
                sys.path.append(os.path.dirname(
                    globruntime(context['runtimepath'],
                                'bin/cpsm_py' + ext)[0]))
                self._initialized = True
            else:
                self.error_message(context,
                                   'matcher/cpsm: bin/cpsm_py' + ext +
                                   ' is not found in your runtimepath.')
                self.error_message(context,
                                   'matcher/cpsm: You must install/build' +
                                   ' Python3 support enabled cpsm.')
                self._disabled = True
                return []

        ispath = (os.path.exists(context['candidates'][0]['word']))
        cpsm_result = self._get_cpsm_result(
            ispath, context['candidates'], context['input'])
        return [x for x in context['candidates'] if x['word'] in cpsm_result]

    def convert_pattern(self, input_str):
        return convert2fuzzy_pattern(input_str)

    def _get_cpsm_result(self, ispath, candidates, pattern):
        import cpsm_py
        return cpsm_py.ctrlp_match((d['word'] for d in candidates),
                                   pattern, limit=1000, ispath=ispath)[0]
