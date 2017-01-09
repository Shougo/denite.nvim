# ============================================================================
# FILE: denite.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.util import get_custom_source, find_rplugins

import denite.source  # noqa
import denite.filter  # noqa
import denite.kind    # noqa

import importlib.machinery
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

        for alias, base in [[x, y] for [x, y] in
                            self.__custom['alias_source'].items()
                            if x not in self.__sources]:
            if base not in self.__sources:
                self.error('Invalid base: ' + base)
                continue
            self.__sources[alias] = copy.copy(self.__sources[base])
            self.__sources[alias].name = alias

    def gather_candidates(self, context):
        for source in self.__current_sources:
            source.context['is_redraw'] = context['is_redraw']
            candidates = source.gather_candidates(source.context)
            source.context['all_candidates'] = candidates
            source.context['candidates'] = candidates

    def filter_candidates(self, context):
        for source in self.__current_sources:
            ctx = source.context
            ctx['input'] = context['input']
            ctx['mode'] = context['mode']
            ctx['is_redraw'] = context['is_redraw']
            entire = ctx['all_candidates']
            if ctx['is_async']:
                entire += source.gather_candidates(ctx)
            if not entire:
                continue
            partial = []
            for i in range(0, len(entire), 1000):
                ctx['candidates'] = entire[i:i+1000]
                for matcher in [self.__filters[x]
                                for x in source.matchers
                                if x in self.__filters]:
                    ctx['candidates'] = matcher.filter(ctx)
                partial += ctx['candidates']
                if len(partial) >= 1000:
                    break
            ctx['candidates'] = partial
            for f in [self.__filters[x]
                      for x in source.sorters + source.converters
                      if x in self.__filters]:
                ctx['candidates'] = f.filter(ctx)
            partial = ctx['candidates']
            for c in partial:
                c['source'] = source.name
            ctx['candidates'] = []
            yield source.name, entire, partial

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
            if not source.context['args']:
                source.context['args'] = get_custom_source(
                    self.__custom, source.name, 'args', [])

            if hasattr(source, 'on_init'):
                source.on_init(source.context)
            self.__current_sources.append(source)

        for filter in [x for x in self.__filters.values()
                       if x.vars and x.name in self.__custom['filter']]:
            filter.vars.update(self.__custom['filter'][filter.name])

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

    def get_source(self, name):
        return self.__sources.get(name, {})

    def get_current_sources(self):
        return self.__current_sources

    def load_sources(self, context):
        # Load sources from runtimepath
        loaded_paths = [x.path for x in self.__sources.values()]
        for path, name in find_rplugins(context, 'source', loaded_paths):
            module = importlib.machinery.SourceFileLoader(
                'denite.source.' + name, path).load_module()
            source = module.Source(self.__vim)
            self.__sources[source.name] = source
            source.path = path
            syntax_name = 'deniteSource_' + source.name.replace('/', '_')
            if not source.syntax_name:
                source.syntax_name = syntax_name

            if source.name in self.__custom['alias_source']:
                # Load alias
                for alias in self.__custom['alias_source'][source.name]:
                    self.__sources[alias] = module.Source(self.__vim)
                    self.__sources[alias].name = alias
                    self.__sources[alias].path = path
                    self.__sources[alias].syntax_name = syntax_name

    def get_filter(self, filter_name):
        return self.__filters.get(filter_name, None)

    def load_filters(self, context):
        # Load filters from runtimepath
        loaded_paths = [x.path for x in self.__filters.values()]
        for path, name in find_rplugins(context, 'filter', loaded_paths):
            module = importlib.machinery.SourceFileLoader(
                'denite.filter.' + name, path).load_module()
            f = module.Filter(self.__vim)
            f.path = path
            self.__filters[name] = f

            if name in self.__custom['alias_filter']:
                # Load alias
                for alias in self.__custom['alias_filter'][name]:
                    self.__filters[alias] = module.Filter(self.__vim)
                    self.__filters[alias].name = alias
                    self.__filters[alias].path = path

    def load_kinds(self, context):
        # Load kinds from runtimepath
        loaded_paths = [x.path for x in self.__kinds.values()]
        for path, name in find_rplugins(context, 'kind', loaded_paths):
            module = importlib.machinery.SourceFileLoader(
                'denite.kind.' + name, path).load_module()
            kind = module.Kind(self.__vim)
            kind.path = path
            self.__kinds[name] = kind

    def do_action(self, context, action_name, targets):
        action = self.get_action(context, action_name, targets)
        if not action:
            return True

        context['targets'] = targets
        return action['func'](context)

    def get_action(self, context, action_name, targets):
        if not targets:
            return {}

        kinds = set()
        for target in targets:
            k = target['kind'] if 'kind' in target else (
                self.__sources[target['source']].kind)
            kinds.add(k)
        if len(kinds) != 1:
            self.error('Multiple kinds are detected')
            return {}

        k = kinds.pop()

        if isinstance(k, str):
            # k is kind name
            if k not in self.__kinds:
                self.error('Invalid kind: ' + k)
                return {}

            kind = self.__kinds[k]
        else:
            kind = k

        if action_name == 'default':
            action_name = context['default_action']
            if action_name == 'default':
                action_name = kind.default_action
        action_attr = 'action_' + action_name
        if not hasattr(kind, action_attr):
            self.error('Invalid action: ' + action_name)
            return {}
        return {
            'name': action_name,
            'func': getattr(kind, action_attr),
            'is_quit': (action_name not in kind.persist_actions),
            'is_redraw': (action_name in kind.redraw_actions),
        }

    def get_actions(self, context, targets):
        if 'kind' in targets:
            kind_name = targets['kind']
        else:
            kind_name = self.__sources[targets[0]['source']].kind

        if not isinstance(kind_name, str):
            kind_name = kind_name.name

        if kind_name not in self.__kinds:
            self.error('Invalid kind: ' + kind_name)
            return []

        kind = self.__kinds[kind_name]
        return ['default'] + [x.replace('action_', '') for x in dir(kind)
                              if x.find('action_') == 0]

    def is_async(self):
        return len([x for x in self.__current_sources
                    if x.context['is_async']]) > 0
