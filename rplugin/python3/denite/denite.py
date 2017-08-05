# ============================================================================
# FILE: denite.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.util import (get_custom_source,
                         find_rplugins, split_input, abspath)

import denite.source  # noqa
import denite.filter  # noqa
import denite.kind    # noqa

import importlib.machinery
import copy
import re
from collections import ChainMap
from itertools import filterfalse


class Denite(object):

    def __init__(self, vim):
        self._vim = vim
        self._sources = {}
        self._filters = {}
        self._kinds = {}
        self._runtimepath = ''
        self._current_sources = []

    def start(self, context):
        self._custom = context['custom']

        if self._vim.options['runtimepath'] != self._runtimepath:
            # Recache
            self.load_sources(context)
            self.load_filters(context)
            self.load_kinds(context)
            self._runtimepath = self._vim.options['runtimepath']

        for alias, base in [[x, y] for [x, y] in
                            self._custom['alias_source'].items()
                            if x not in self._sources]:
            if base not in self._sources:
                self.error('Invalid base: ' + base)
                continue
            self._sources[alias] = copy.copy(self._sources[base])
            self._sources[alias].name = alias

    def gather_candidates(self, context):
        for source in self._current_sources:
            ctx = source.context
            ctx['is_redraw'] = context['is_redraw']
            ctx['messages'] = context['messages']
            ctx['mode'] = context['mode']
            ctx['input'] = context['input']
            ctx['prev_input'] = context['input']
            ctx['event'] = 'gather'
            ctx['async_timeout'] = 0.01
            ctx['path'] = abspath(self._vim, context['path'])

            candidates = self._gather_source_candidates(
                source.context, source)

            ctx['all_candidates'] = candidates
            ctx['candidates'] = candidates

            context['messages'] = ctx['messages']

    def _gather_source_candidates(self, context, source):
        max_len = int(context['max_candidate_width']) * 2
        candidates = source.gather_candidates(context)
        for candidate in [x for x in candidates if len(x['word']) > max_len]:
            candidate['word'] = candidate['word'][: max_len]
        return candidates

    def filter_candidates(self, context):
        for source in self._current_sources:
            ctx = source.context
            ctx['matchers'] = context['matchers']
            ctx['input'] = context['input']
            if context['smartcase']:
                ctx['ignorecase'] = re.search(r'[A-Z]', ctx['input']) is None
            ctx['mode'] = context['mode']
            ctx['async_timeout'] = 0.03 if ctx['mode'] != 'insert' else 0.02
            if ctx['prev_input'] != ctx['input'] and ctx['is_interactive']:
                ctx['event'] = 'interactive'
                ctx['all_candidates'] = self._gather_source_candidates(
                    ctx, source)
            ctx['prev_input'] = ctx['input']
            entire = ctx['all_candidates']
            if ctx['is_async']:
                ctx['event'] = 'async'
                entire += self._gather_source_candidates(ctx, source)
            if not entire:
                yield source.name, entire, [], []
                continue
            partial = []
            ctx['candidates'] = entire
            for i in range(0, len(entire), 1000):
                ctx['candidates'] = entire[i:i+1000]
                matchers = [self._filters[x] for x in
                            (ctx['matchers'].split(',') if ctx['matchers']
                             else source.matchers)
                            if x in self._filters]
                self.match_candidates(ctx, matchers)
                partial += ctx['candidates']
                if len(partial) >= 1000:
                    break
            ctx['candidates'] = partial
            for f in [self._filters[x]
                      for x in source.sorters + source.converters
                      if x in self._filters]:
                ctx['candidates'] = f.filter(ctx)
            partial = ctx['candidates']
            for c in partial:
                c['source'] = source.name
            ctx['candidates'] = []

            patterns = filterfalse(lambda x: x == '', (
                self._filters[x].convert_pattern(context['input'])
                for x in source.matchers if self._filters[x]))

            yield source.name, entire, partial, patterns

    def match_candidates(self, context, matchers):
        for pattern in split_input(context['input']):
            ctx = copy.copy(context)
            if pattern and pattern[0] == '!':
                if pattern == '!':
                    continue
                ctx['input'] = pattern[1:]
                ignore = self.call_matchers(ctx, matchers)
                context['candidates'] = [x for x in context['candidates']
                                         if x not in ignore]
            else:
                ctx['input'] = pattern
                context['candidates'] = self.call_matchers(ctx, matchers)

    def call_matchers(self, ctx, matchers):
        for matcher in matchers:
            ctx['candidates'] = matcher.filter(ctx)
        return ctx['candidates']

    def on_init(self, context):
        self._current_sources = []
        for [name, args] in [[x['name'], x['args']]
                             for x in context['sources']]:
            if name not in self._sources:
                raise NameError('Source "' + name + '" is not found.')

            source = copy.copy(self._sources[name])
            source.context = copy.copy(context)
            source.context['args'] = args
            source.context['is_async'] = False
            source.context['is_interactive'] = False
            source.context['all_candidates'] = []
            source.context['candidates'] = []

            # Set the source attributes.
            source.matchers = get_custom_source(
                self._custom, source.name,
                'matchers', source.matchers)
            source.sorters = get_custom_source(
                self._custom, source.name,
                'sorters', source.sorters)
            source.converters = get_custom_source(
                self._custom, source.name,
                'converters', source.converters)
            source.vars.update(
                get_custom_source(self._custom, source.name,
                                  'vars', source.vars))
            if not source.context['args']:
                source.context['args'] = get_custom_source(
                    self._custom, source.name, 'args', [])

            if hasattr(source, 'on_init'):
                source.on_init(source.context)
            self._current_sources.append(source)

        for filter in [x for x in self._filters.values()
                       if x.vars and x.name in self._custom['filter']]:
            filter.vars.update(self._custom['filter'][filter.name])

    def on_close(self, context):
        for source in self._current_sources:
            if hasattr(source, 'on_close'):
                source.on_close(source.context)

    def debug(self, expr):
        denite.util.debug(self._vim, expr)

    def error(self, msg):
        self._vim.call('denite#util#print_error', msg)

    def get_current_sources(self):
        return self._current_sources

    def load_sources(self, context):
        # Load sources from runtimepath
        loaded_paths = [x.path for x in self._sources.values()]
        for path, name in find_rplugins(context, 'source', loaded_paths):
            module = importlib.machinery.SourceFileLoader(
                'denite.source.' + name, path).load_module()
            source = module.Source(self._vim)
            self._sources[source.name] = source
            source.path = path
            syntax_name = 'deniteSource_' + source.name.replace('/', '_')
            if not source.syntax_name:
                source.syntax_name = syntax_name

            if source.name in self._custom['alias_source']:
                # Load alias
                for alias in self._custom['alias_source'][source.name]:
                    self._sources[alias] = module.Source(self._vim)
                    self._sources[alias].name = alias
                    self._sources[alias].path = path
                    self._sources[alias].syntax_name = syntax_name

    def load_filters(self, context):
        # Load filters from runtimepath
        loaded_paths = [x.path for x in self._filters.values()]
        for path, name in find_rplugins(context, 'filter', loaded_paths):
            module = importlib.machinery.SourceFileLoader(
                'denite.filter.' + name, path).load_module()
            f = module.Filter(self._vim)
            f.path = path
            self._filters[name] = f

            if name in self._custom['alias_filter']:
                # Load alias
                for alias in self._custom['alias_filter'][name]:
                    self._filters[alias] = module.Filter(self._vim)
                    self._filters[alias].name = alias
                    self._filters[alias].path = path

    def load_kinds(self, context):
        # Load kinds from runtimepath
        loaded_paths = [x.path for x in self._kinds.values()]
        for path, name in find_rplugins(context, 'kind', loaded_paths):
            module = importlib.machinery.SourceFileLoader(
                'denite.kind.' + name, path).load_module()
            kind = module.Kind(self._vim)
            kind.path = path
            self._kinds[name] = kind

    def do_action(self, context, action_name, targets):
        action = self.get_action(context, action_name, targets)
        if not action:
            return True

        sources = set()
        for target in targets:
            sources.add(target['source'])
        context['source'] = self._sources[
            sources.pop()].context if len(sources) == 1 else {}

        context['targets'] = targets
        return action['func'](context) if action['func'] else self._vim.call(
            'denite#custom#call_action',
            action['kind'], action['name'], context)

    def _get_kind(self, context, targets):
        if not targets:
            return {}

        kinds = set()
        for target in targets:
            k = target['kind'] if 'kind' in target else (
                self._sources[target['source']].kind)
            kinds.add(k)
        if len(kinds) != 1:
            self.error('Multiple kinds are detected')
            return {}

        k = kinds.pop()

        if isinstance(k, str):
            # k is kind name
            if k not in self._kinds:
                self.error('Invalid kind: ' + k)
                return {}

            kind = self._kinds[k]
        else:
            kind = k

        return kind

    def _get_source(self, context, targets):
        if not targets:
            return {}

        sources = set()
        for target in targets:
            sources.add(self._sources[target['source']])
        if len(sources) != 1:
            self.error('Multiple sources are detected')
            return {}
        return sources.pop()

    def get_action(self, context, action_name, targets):
        kind = self._get_kind(context, targets)
        if not kind:
            return {}

        source = self._get_source(context, targets)
        if not source:
            return {}

        if action_name == 'default':
            action_name = context['default_action']
            if action_name == 'default':
                action_name = source.default_action
            if action_name == 'default':
                action_name = kind.default_action

        # Custom action
        custom_actions = self.get_custom_actions(kind.name)
        if action_name in custom_actions:
            _, user_attrs = custom_actions[action_name]
            return ChainMap(user_attrs, {
                'name': action_name,
                'kind': kind.name,
                'func': None,
                'is_quit': True,
                'is_redraw': False,
            })

        action_attr = 'action_' + action_name
        if not hasattr(kind, action_attr):
            self.error('Invalid action: ' + action_name)
            return {}
        return {
            'name': action_name,
            'kind': kind.name,
            'func': getattr(kind, action_attr),
            'is_quit': (action_name not in kind.persist_actions),
            'is_redraw': (action_name in kind.redraw_actions),
        }

    def get_custom_actions(self, kind_name):
        actions = {}
        if '_' in self._custom['action']:
            actions.update(self._custom['action']['_'])
        if kind_name in self._custom['action']:
            actions.update(self._custom['action'][kind_name])
        return actions

    def get_action_names(self, context, targets):
        kind = self._get_kind(context, targets)
        if not kind:
            return []
        actions = kind.get_action_names()
        actions += self.get_custom_actions(kind.name).keys()
        return actions

    def is_async(self):
        return len([x for x in self._current_sources
                    if x.context['is_async']]) > 0
