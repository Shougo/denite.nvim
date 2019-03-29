# ============================================================================
# FILE: child.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from denite.util import (
    get_custom_source, debug, regex_convert_str_vim,
    import_rplugins, expand, split_input, abspath)

import copy
import os
import re
import time
from os.path import normpath, normcase
from collections import ChainMap
from itertools import filterfalse


class Child(object):

    def __init__(self, vim):
        self._vim = vim
        self._sources = {}
        self._filters = {}
        self._kinds = {}
        self._runtimepath = ''
        self._current_sources = []

    def main(self, name, args, queue_id):
        ret = None
        if name == 'start':
            self.start(args[0])
        elif name == 'gather_candidates':
            self.gather_candidates(args[0])
        elif name == 'on_init':
            self.on_init(args[0])
        elif name == 'on_close':
            self.on_close(args[0])
        elif name == 'init_syntax':
            self.init_syntax(args[0], args[1])
        elif name == 'filter_candidates':
            ret = self.filter_candidates(args[0])
        elif name == 'do_action':
            ret = self.do_action(args[0], args[1], args[2])
        elif name == 'get_action':
            ret = self.get_action(args[0], args[1], args[2])
        elif name == 'get_action_names':
            ret = self.get_action_names(args[0], args[1])
        elif name == 'is_async':
            ret = self.is_async()
        return ret

    def start(self, context):
        self._custom = context['custom']

        if self._vim.options['runtimepath'] != self._runtimepath:
            # Recache
            self._load_sources(context)
            self._load_filters(context)
            self._load_kinds(context)
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
            ctx['error_messages'] = context['error_messages']
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

    def on_init(self, context):
        self._current_sources = []
        index = 0
        for [name, args] in [[x['name'], x['args']]
                             for x in context['sources']]:
            if name not in self._sources:
                raise NameError('Source "' + name + '" is not found.')

            source = copy.copy(self._sources[name])
            source.context = copy.copy(context)
            source.context['args'] = args
            source.context['is_async'] = False
            source.context['is_skipped'] = False
            source.context['is_interactive'] = False
            source.context['all_candidates'] = []
            source.context['candidates'] = []
            source.context['prev_time'] = time.time()
            source.index = index

            # Set the source attributes.
            self._set_source_attribute(source, 'matchers')
            self._set_source_attribute(source, 'sorters')
            self._set_source_attribute(source, 'converters')
            self._set_source_attribute(source, 'max_candidates')
            source.vars.update(
                get_custom_source(self._custom, source.name,
                                  'vars', source.vars))
            if not source.context['args']:
                source.context['args'] = get_custom_source(
                    self._custom, source.name, 'args', [])

            if hasattr(source, 'on_init'):
                source.on_init(source.context)
            self._current_sources.append(source)
            index += 1

        for filter in [x for x in self._filters.values()
                       if x.vars and x.name in self._custom['filter']]:
            filter.vars.update(self._custom['filter'][filter.name])

    def on_close(self, context):
        for source in self._current_sources:
            if hasattr(source, 'on_close'):
                source.on_close(source.context)

    def init_syntax(self, context, is_multi):
        for source in self._current_sources:
            name = re.sub('[^a-zA-Z0-9_]', '_', source.name)
            source_name = self._get_display_source_name(
                context, is_multi, source.name)

            self._vim.command(
                'highlight default link ' +
                'deniteSourceLine_' + name +
                ' Type'
            )

            syntax_line = ('syntax match %s /^ %s/ nextgroup=%s keepend' +
                           ' contains=deniteConcealedMark') % (
                'deniteSourceLine_' + name,
                regex_convert_str_vim(source_name) +
                               (' ' if source_name else ''),
                source.syntax_name,
            )
            self._vim.command(syntax_line)
            source.highlight()
            source.define_syntax()

    def filter_candidates(self, context):
        pattern = ''
        statuses = []
        candidates = []
        for status, partial, patterns in self._filter_candidates(context):
            candidates += partial
            statuses.append(status)

            if pattern == '' and patterns:
                pattern = next(patterns, '')

        if context['sorters']:
            for sorter in context['sorters'].split(','):
                ctx = copy.copy(context)
                ctx['candidates'] = candidates
                candidates = self._filters[sorter].filter(ctx)

        if context['unique']:
            unique_candidates = []
            unique_words = set()
            for candidate in candidates:
                # Normalize file paths
                word = candidate['word']
                if word.startswith('~') and os.path.exists(
                        os.path.expanduser(word)):
                    word = os.path.expanduser(word)
                if os.path.exists(word):
                    word = os.path.abspath(word)
                if word not in unique_words:
                    unique_words.add(word)
                    unique_candidates.append(candidate)
            candidates = unique_candidates
        if context['reversed']:
            candidates.reverse()
        if self.is_async():
            statuses.append('[async]')
        return (pattern, statuses, candidates)

    def do_action(self, context, action_name, targets):
        action = self.get_action(context, action_name, targets)
        if not action:
            return True

        for target in targets:
            source = self._current_sources[int(target['source_index'])]
            target['source_context'] = {
                k: v for k, v in
                source.context.items()
                if k.startswith('__')
            } if source.is_public_context else {}

        context['targets'] = targets
        return action['func'](context) if action['func'] else self._vim.call(
            'denite#custom#_call_action',
            action['kind'], action['name'], context)

    def get_action(self, context, action_name, targets):
        actions = set()
        action = None
        for target in targets:
            action = self._get_action(context, action_name, target)
            if action:
                actions.add(action['name'])
        if len(actions) > 1:
            self.error('Multiple actions are detected: ' + action_name)
            return {}
        return action if actions else {}

    def get_action_names(self, context, targets):
        kinds = set()
        for target in targets:
            k = self._get_kind(context, target)
            if k:
                kinds.add(k)
        if len(kinds) != 1:
            if len(kinds) > 1:
                self.error('Multiple kinds are detected')
            return []

        kind = kinds.pop()
        actions = kind.get_action_names()
        actions += self._get_custom_actions(kind.name).keys()
        return actions

    def is_async(self):
        return len([x for x in self._current_sources
                    if x.context['is_async'] or x.context['is_skipped']
                    ]) > 0

    def debug(self, expr):
        debug(self._vim, expr)

    def error(self, msg):
        self._vim.call('denite#util#print_error', msg)
        self._vim.call('denite#util#getchar')

    def _filter_candidates(self, context):
        for source in self._current_sources:
            ctx = source.context
            ctx['matchers'] = context['matchers']
            ctx['input'] = context['input']
            if context['expand']:
                ctx['input'] = expand(ctx['input'])
            if context['smartcase']:
                ctx['ignorecase'] = re.search(r'[A-Z]', ctx['input']) is None
            ctx['mode'] = context['mode']
            ctx['async_timeout'] = 0.03 if ctx['mode'] != 'insert' else 0.02
            if ctx['prev_input'] != ctx['input']:
                ctx['prev_time'] = time.time()
                if ctx['is_interactive']:
                    ctx['event'] = 'interactive'
                    ctx['all_candidates'] = self._gather_source_candidates(
                        ctx, source)
            ctx['prev_input'] = ctx['input']
            entire = ctx['all_candidates']
            if ctx['is_async']:
                ctx['event'] = 'async'
                entire += self._gather_source_candidates(ctx, source)
            if len(entire) > 20000 and (time.time() - ctx['prev_time'] <
                                        int(context['skiptime']) / 1000.0):
                ctx['is_skipped'] = True
                yield self._get_source_status(
                    ctx, source, entire, []), [], []
                continue
            if not entire:
                yield self._get_source_status(
                    ctx, source, entire, []), [], []
                continue

            ctx['is_skipped'] = False
            partial = []
            ctx['candidates'] = entire
            for i in range(0, len(entire), 1000):
                ctx['candidates'] = entire[i:i+1000]
                matchers = [self._filters[x] for x in
                            (ctx['matchers'].split(',') if ctx['matchers']
                             else source.matchers)
                            if x in self._filters]
                self._match_candidates(ctx, matchers)
                partial += ctx['candidates']
                if len(partial) >= source.max_candidates:
                    break
            ctx['candidates'] = partial
            for f in [self._filters[x]
                      for x in source.sorters + source.converters
                      if x in self._filters]:
                ctx['candidates'] = f.filter(ctx)
            partial = ctx['candidates'][: source.max_candidates]
            for c in partial:
                c['source_name'] = source.name
                c['source_index'] = source.index
            ctx['candidates'] = []

            patterns = filterfalse(lambda x: x == '', (
                self._filters[x].convert_pattern(ctx['input'])
                for x in source.matchers if self._filters[x]))

            yield self._get_source_status(
                ctx, source, entire, partial), partial, patterns

    def _gather_source_candidates(self, context, source):
        max_len = int(context['max_candidate_width']) * 2
        candidates = source.gather_candidates(context)
        for candidate in [x for x in candidates if len(x['word']) > max_len]:
            candidate['word'] = candidate['word'][: max_len]
        return candidates

    def _get_source_status(self, context, source, entire, partial):
        return (source.get_status(context) if not partial else
                f'{source.get_status(context)}'
                f'({len(partial)}/{len(entire)})')

    def _match_candidates(self, context, matchers):
        for pattern in split_input(context['input']):
            ctx = copy.copy(context)
            if pattern and pattern[0] == '!':
                if pattern == '!':
                    continue
                ctx['input'] = pattern[1:]
                ignore = self._call_matchers(ctx, matchers)
                context['candidates'] = [x for x in context['candidates']
                                         if x not in ignore]
            else:
                ctx['input'] = pattern
                context['candidates'] = self._call_matchers(ctx, matchers)

    def _call_matchers(self, ctx, matchers):
        for matcher in matchers:
            ctx['candidates'] = matcher.filter(ctx)
        return ctx['candidates']

    def _set_source_attribute(self, source, attr):
        source_attr = getattr(source, attr)
        setattr(source, attr, get_custom_source(
            self._custom, source.name, attr, source_attr))

    def _load_sources(self, context):
        # Load sources from runtimepath
        # Note: load "denite.source" for old sources compatibility
        import denite.source # noqa
        rplugins = import_rplugins('Source', context, 'source', [
            normcase(normpath(x.path))
            for x in self._sources.values()
        ])
        for Source, path, _ in rplugins:
            source = Source(self._vim)
            self._sources[source.name] = source
            source.path = path
            syntax_name = 'deniteSource_' + source.name.replace('/', '_')
            if not source.syntax_name:
                source.syntax_name = syntax_name

            if source.name in self._custom['alias_source']:
                # Load alias
                for alias in self._custom['alias_source'][source.name]:
                    self._sources[alias] = Source(self._vim)
                    self._sources[alias].name = alias
                    self._sources[alias].path = path
                    self._sources[alias].syntax_name = syntax_name
        # Update source_names for completion
        self._vim.call(
            'denite#helper#_set_available_sources',
            list(self._sources.keys()),
        )

    def _load_filters(self, context):
        # Load filters from runtimepath
        rplugins = import_rplugins('Filter', context, 'filter', [
            normcase(normpath(x.path))
            for x in self._filters.values()
        ])
        for Filter, path, module_path in rplugins:
            f = Filter(self._vim)
            # NOTE:
            # Previously, kind and filter but source uses
            # module_path as name so modules which does not
            # have proper 'name' may worked.
            # So add 'name' attribute to the class if that
            # attribute does not exist for the backward
            # compatibility
            if not hasattr(f, 'name') or not f.name:
                # Prefer foo/bar instead of foo.bar in name
                setattr(f, 'name', module_path.replace('.', '/'))
            f.path = path
            self._filters[f.name] = f

            if f.name not in self._custom['alias_filter']:
                self._custom['alias_filter'][f.name] = []
            alias_filter = self._custom['alias_filter'][f.name]

            if '/' in f.name:
                alias_filter.append(f.name.replace('/', '_'))

            # Load alias
            for alias in alias_filter:
                self._filters[alias] = Filter(self._vim)
                self._filters[alias].name = alias
                self._filters[alias].path = path

    def _load_kinds(self, context):
        # Load kinds from runtimepath
        rplugins = import_rplugins('Kind', context, 'kind', [
            normcase(normpath(x.path))
            for x in self._kinds.values()
        ])
        for Kind, path, module_path in rplugins:
            kind = Kind(self._vim)
            # NOTE:
            # Previously, kind and filter but source uses
            # module_path as name so modules which does not
            # have proper 'name' may worked.
            # So add 'name' attribute to the class if that
            # attribute does not exist for the backward
            # compatibility
            if not hasattr(kind, 'name') or not kind.name:
                # Prefer foo/bar instead of foo.bar in name
                setattr(kind, 'name', module_path.replace('.', '/'))
            kind.path = path
            self._kinds[kind.name] = kind

    def _get_kind(self, context, target):
        k = target['kind'] if 'kind' in target else (
                self._current_sources[int(target['source_index'])].kind)

        if isinstance(k, str):
            # k is kind name
            if k not in self._kinds:
                self.error('Invalid kind: ' + k)
                return {}

            kind = self._kinds[k]
        else:
            kind = k

        return kind

    def _get_action(self, context, action_name, target):
        kind = self._get_kind(context, target)
        if not kind:
            return {}

        source = self._current_sources[int(target['source_index'])]

        if action_name == 'default':
            action_name = context['default_action']
            if action_name == 'default':
                action_name = source.default_action
            if action_name == 'default':
                action_name = kind.default_action

        # Custom action
        custom_actions = self._get_custom_actions(kind.name)
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

    def _get_custom_actions(self, kind_name):
        actions = {}
        if '_' in self._custom['action']:
            actions.update(self._custom['action']['_'])
        if kind_name in self._custom['action']:
            actions.update(self._custom['action'][kind_name])
        return actions

    def _get_display_source_name(self, context, is_multi, name):
        source_names = context['source_names']
        if not is_multi or source_names == 'hide':
            source_name = ''
        else:
            short_name = (re.sub(r'([a-zA-Z])[a-zA-Z]+', r'\1', name)
                          if re.search(r'[^a-zA-Z]', name) else name[:2])
            source_name = short_name if source_names == 'short' else name
        return source_name
