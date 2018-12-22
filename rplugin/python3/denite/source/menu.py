# ============================================================================
# FILE: menu.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
#         TJ DeVries <devries.timothyj at gmail.com>
# License: MIT license
# ============================================================================

from denite.source.base import Base


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'menu'
        self.kind = 'command'

        # self.matchers = []
        # self.sorters = []

        self.vars = {
            'menus': {},
            'unite_source_menu_compatibility': False,
        }

    def on_init(self, context):
        if self.vars['unite_source_menu_compatibility']:
            self.vars['menus'].update(
                self.vim.vars['unite_source_menu_menus']
            )

    def filter_candidates(self, candidates, file_type=None):
        if file_type:
            return [candidate for candidate in candidates
                    if (len(candidate) < 3 or
                        file_type in candidate[2].split(','))]

        return candidates

    def gather_candidates(self, context):
        # If no menus have been defined, just exit
        if 'menus' not in self.vars or self.vars['menus'] == {}:
            return []

        lines = []
        menus = self.vars['menus']
        args = context['args']
        file_type = self.vim.command_output('silent echo &ft')

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
                            menus[menu]['file_candidates'], file_type)
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
                            menus[menu]['command_candidates'], file_type)
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
                                'directory_candidates'], file_type)
                        ])
        else:
            # Display all the registered menus
            lines.extend([
                {
                    'word': '{} - {}'.format(
                        menu, candidate.get('description')),
                    'kind': 'command',
                    'action__command': 'Denite menu:' + menu,
                 }
                for menu, candidate in menus.items()
            ])

        return lines
