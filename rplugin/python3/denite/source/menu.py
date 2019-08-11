# ============================================================================
# FILE: menu.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
#         TJ DeVries <devries.timothyj at gmail.com>
# License: MIT license
# ============================================================================

import typing

from denite.base.source import Base
from denite.util import Nvim, UserContext, Candidates


class Source(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'menu'
        self.kind = 'command'

        # self.matchers = []
        # self.sorters = []

        self.vars = {
            'menus': {},
            'unite_source_menu_compatibility': False,
        }

    def on_init(self, context: UserContext) -> None:
        if self.vars['unite_source_menu_compatibility']:
            self.vars['menus'].update(
                self.vim.vars['unite_source_menu_menus']
            )

    def filter_candidates(self, candidates: typing.Any,
                          filetype: str = '') -> typing.Any:
        if not filetype:
            return candidates

        return [candidate for candidate in candidates
                if len(candidate) < 3 or filetype in candidate[2].split(',')]

    def gather_candidates(self, context: UserContext) -> Candidates:
        # If no menus have been defined, just exit
        if 'menus' not in self.vars or self.vars['menus'] == {}:
            return []

        lines = []
        menus = self.vars['menus']
        args = context['args']
        filetype = context['filetype']

        if args:
            # Loop through each menu option
            for menu in args:
                # If a menu doesn't exist, just continue gracefully
                if menu not in menus:
                    continue

                # Handle file candidates
                if 'file_candidates' in menus[menu]:
                    lines.extend([
                        {'word': str(candidate[0]),
                         'kind': 'file',
                         'action__path': candidate[1],
                         }
                        for candidate in self.filter_candidates(
                            menus[menu]['file_candidates'], filetype)
                    ])

                # Handle command candidates
                if 'command_candidates' in menus[menu]:
                    lines.extend([
                        {
                            'word': str(candidate[0]),
                            'kind': 'command',
                            'action__command': candidate[1]
                         }
                        for candidate in self.filter_candidates(
                            menus[menu]['command_candidates'], filetype)
                    ])
                # Handle directory candidates
                if 'directory_candidates' in menus[menu]:
                    lines.extend([
                        {
                            'word': str(candidate[0]),
                            'kind': 'directory',
                            'action__path': candidate[1]
                         }
                        for candidate in self.filter_candidates(menus[menu][
                                'directory_candidates'], filetype)
                        ])
        else:
            # Display all the registered menus
            max_menu = max([self.vim.call('strwidth', x)
                            for x in menus.keys()])
            word_format = '{0:<' + str(max_menu) + '} - {1}'
            lines.extend([
                {
                    'word': word_format.format(
                        menu, candidate.get('description')),
                    'kind': 'source',
                    'action__source': ['menu', menu],
                 }
                for menu, candidate in menus.items()
            ])

        return lines
