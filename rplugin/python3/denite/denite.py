# ============================================================================
# FILE: denite.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.util import globruntime, get_custom_source

import denite.source  # noqa
import denite.filter  # noqa
import denite.kind    # noqa

import importlib.machinery
import os.path
import copy


class Denite(object):

    def __init__(self, vim):
        self.__vim = vim
        self.__sources = {}
        self.__current_sources = []
        self.__filters = {}
        self.__kinds = {}
        self.__runtimepath = ''

    def start(self, context):
        self.__custom = context['custom']

        if self.__vim.options['runtimepath'] != self.__runtimepath:
            # Recache
            self.load_sources()
            self.load_filters()
            self.load_kinds()
            self.__runtimepath = self.__vim.options['runtimepath']

    def gather_candidates(self, context):
        for source in self.__current_sources:
            candidates = []
            for c in source.gather_candidates(source.context):
                c['source'] = source.name
                candidates.append(c)
            source.context['all_candidates'] = candidates

    def filter_candidates(self, context):
        for source in self.__current_sources:
            source.context['input'] = context['input']
            source.context['candidates'] = copy.copy(
                source.context['all_candidates'])
            for filter in [self.__filters[x]
                           for x in source.matchers +
                           source.sorters + source.converters
                           if x in self.__filters]:
                source.context['candidates'] = filter.filter(source.context)
            candidates = source.context['candidates']
            source.context['candidates'] = []
            yield source.name, candidates

    def on_init(self, context):
        self.__current_sources = []
        for [name, args] in [[x['name'], x['args']]
                             for x in context['sources']]:
            if name not in self.__sources:
                self.error('Source "' + name + '" is not found.')
                continue
            source = self.__sources[name]
            source.context = copy.deepcopy(context)
            source.context['args'] = args

            if hasattr(source, 'on_init'):
                source.on_init(source.context)
            self.__current_sources.append(source)

    def debug(self, expr):
        denite.util.debug(self.__vim, expr)

    def error(self, msg):
        self.__vim.call('denite#util#print_error', msg)

    def get_sources(self):
        return self.__sources

    def load_sources(self):
        # Load sources from runtimepath
        for path in globruntime(self.__vim,
                                'rplugin/python3/denite/source/base.py'
                                ) + globruntime(
                                    self.__vim,
                                    'rplugin/python3/denite/source/*.py'):
            name = os.path.basename(path)[: -3]
            module = importlib.machinery.SourceFileLoader(
                'denite.source.' + name, path).load_module()
            if not hasattr(module, 'Source') or name in self.__sources:
                continue

            source = module.Source(self.__vim)

            # Set the source attributes.
            source.matchers = get_custom_source(
                self.__custom, source.name,
                'matchers', source.matchers)
            source.sorters = get_custom_source(
                self.__custom, source.name,
                'sorters', source.sorters)
            source.converters = get_custom_source(
                self.__custom, source.name,
                'converters', source.converters)
            source.vars = get_custom_source(
                self.__custom, source.name,
                'vars', source.vars)

            self.__sources[source.name] = source

    def load_filters(self):
        # Load filters from runtimepath
        for path in globruntime(self.__vim,
                                'rplugin/python3/denite/filter/base.py'
                                ) + globruntime(
                                    self.__vim,
                                    'rplugin/python3/denite/filter/*.py'):
            name = os.path.basename(path)[: -3]
            filter = importlib.machinery.SourceFileLoader(
                'denite.filter.' + name, path).load_module()
            if hasattr(filter, 'Filter') and name not in self.__filters:
                self.__filters[name] = filter.Filter(self.__vim)

    def load_kinds(self):
        # Load kinds from runtimepath
        for path in globruntime(self.__vim,
                                'rplugin/python3/denite/kind/base.py'
                                ) + globruntime(
                                    self.__vim,
                                    'rplugin/python3/denite/kind/*.py'):
            name = os.path.basename(path)[: -3]
            kind = importlib.machinery.SourceFileLoader(
                'denite.kind.' + name, path).load_module()
            if hasattr(kind, 'Kind') and name not in self.__kinds:
                self.__kinds[name] = kind.Kind(self.__vim)

    def do_action(self, context, kind, action, targets):
        if kind not in self.__kinds:
            self.error('Invalid kind: ' + kind)
            return

        action_name = 'action_' + action
        if not hasattr(self.__kinds[kind], action_name):
            self.error('Invalid action: ' + action)
            return

        context['targets'] = targets
        func = getattr(self.__kinds[kind], action_name)
        func(context)
