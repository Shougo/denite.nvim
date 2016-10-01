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
        self.__filters = {}
        self.__kinds = {}
        self.__runtimepath = ''
        self.__current_sources = []

    def start(self, context):
        self.__custom = context['custom']

        if self.__vim.options['runtimepath'] != self.__runtimepath:
            # Recache
            self.load_sources(context)
            self.load_filters(context)
            self.load_kinds(context)
            self.__runtimepath = self.__vim.options['runtimepath']

    def gather_candidates(self, context):
        for source in self.__current_sources:
            candidates = source.gather_candidates(source.context)
            source.context['all_candidates'] = candidates
            source.context['candidates'] = candidates

    def filter_candidates(self, context):
        for source in self.__current_sources:
            ctx = source.context
            ctx['input'] = context['input']
            all = ctx['all_candidates']
            if ctx['is_async']:
                all += source.gather_candidates(ctx)
            for i in range(0, len(all), 1000):
                ctx['candidates'] = all[i:i+1000]
                for matcher in [self.__filters[x]
                                for x in source.matchers
                                if x in self.__filters]:
                    ctx['candidates'] = matcher.filter(ctx)
                if len(ctx['candidates']) >= 1000:
                    break
            for filter in [self.__filters[x]
                           for x in source.sorters + source.converters
                           if x in self.__filters]:
                ctx['candidates'] = filter.filter(ctx)
            candidates = ctx['candidates']
            for c in candidates:
                c['source'] = source.name
            ctx['candidates'] = []
            yield source.name, all, candidates

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
            source.context['is_async'] = False
            source.context['all_candidates'] = []
            source.context['candidates'] = []

            if hasattr(source, 'on_init'):
                source.on_init(source.context)
            self.__current_sources.append(source)

    def on_close(self, context):
        for source in self.__current_sources:
            if hasattr(source, 'on_close'):
                source.on_close(source.context)

    def debug(self, expr):
        denite.util.debug(self.__vim, expr)

    def error(self, msg):
        self.__vim.call('denite#util#print_error', msg)

    def get_sources(self):
        return self.__sources

    def load_sources(self, context):
        # Load sources from runtimepath
        rtps = globruntime(
            context['runtimepath'],
            'rplugin/python3/denite/source/base.py')
        rtps.extend(globruntime(context['runtimepath'],
                                'rplugin/python3/denite/source/*.py'))
        for path in rtps:
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
            source.vars.update(
                get_custom_source(self.__custom, source.name,
                                  'vars', source.vars))

            self.__sources[source.name] = source

    def load_filters(self, context):
        # Load filters from runtimepath
        rtps = globruntime(
            context['runtimepath'],
            'rplugin/python3/denite/filter/base.py')
        rtps.extend(globruntime(context['runtimepath'],
                                'rplugin/python3/denite/filter/*.py'))
        for path in rtps:
            name = os.path.basename(path)[: -3]
            filter = importlib.machinery.SourceFileLoader(
                'denite.filter.' + name, path).load_module()
            if hasattr(filter, 'Filter') and name not in self.__filters:
                self.__filters[name] = filter.Filter(self.__vim)

    def load_kinds(self, context):
        # Load kinds from runtimepath
        rtps = globruntime(
            context['runtimepath'],
            'rplugin/python3/denite/kind/base.py')
        rtps.extend(globruntime(context['runtimepath'],
                                'rplugin/python3/denite/kind/*.py'))
        for path in rtps:
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

    def is_async(self):
        return len([x for x in self.__current_sources
                    if x.context['is_async']]) > 0

    def get_current_dir(self):
        for x in self.__current_sources:
            if '__current_dir' in x.context:
                return x.context['__current_dir']
