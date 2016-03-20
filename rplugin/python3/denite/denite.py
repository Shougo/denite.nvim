# ============================================================================
# FILE: denite.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.util import globruntime, get_custom

import denite.sources
import denite.filters

import importlib.machinery
import os.path
import copy

denite.sources  # silence pyflakes
denite.filters  # silence pyflakes


class Denite(object):

    def __init__(self, vim):
        self.__vim = vim
        self.__filters = {}
        self.__sources = {}
        self.__runtimepath = ''

    def start(self):
        if self.__vim.options['runtimepath'] != self.__runtimepath:
            # Recache
            self.load_sources()
            self.load_filters()
            self.__runtimepath = self.__vim.options['runtimepath']

    def gather_candidates(self, context):
        sources = self.__sources.items()
        results = []
        for source_name, source in sources:
            cont = copy.deepcopy(context)

            cont['candidates'] = source.gather_candidates(context)
            results += cont['candidates']
        return results

    def debug(self, expr):
        denite.util.debug(self.__vim, expr)

    def error(self, msg):
        self.__vim.call('denite#util#print_error', msg)

    def load_sources(self):
        # Load sources from runtimepath
        for path in globruntime(self.__vim,
                                'rplugin/python3/denite/sources/base.py'
                                ) + globruntime(
                                    self.__vim,
                                    'rplugin/python3/denite/sources/*.py'):
            name = os.path.basename(path)[: -3]
            module = importlib.machinery.SourceFileLoader(
                'denite.sources.' + name, path).load_module()
            if not hasattr(module, 'Source') or name in self.__sources:
                continue

            source = module.Source(self.__vim)

            # Set the source attributes.
            source.matchers = get_custom(
                self.__vim, source.name).get('matchers', source.matchers)
            source.sorters = get_custom(self.__vim, source.name).get(
                'sorters', source.sorters)
            source.converters = get_custom(self.__vim, source.name).get(
                'converters', source.converters)

            self.__sources[name] = source

    def load_filters(self):
        # Load filters from runtimepath
        for path in globruntime(self.__vim,
                                'rplugin/python3/denite/filters/base.py'
                                ) + globruntime(
                                    self.__vim,
                                    'rplugin/python3/denite/filters/*.py'):
            name = os.path.basename(path)[: -3]
            filter = importlib.machinery.SourceFileLoader(
                'denite.filters.' + name, path).load_module()
            if hasattr(filter, 'Filter') and name not in self.__filters:
                self.__filters[name] = filter.Filter(self.__vim)
