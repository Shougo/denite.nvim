# ============================================================================
# FILE: menu.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
#         TJ DeVries <devries.timothyj at gmail.com>
# License: MIT license
# ============================================================================

from .base import Base


class Source(Base):

    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'menu'
        self.kind = 'jump_list'

        # self.matchers = []
        # self.sorters = []

        self.vars = {
            'menus': {},
            'unite_source_menu_compatibility': False,
        }

    def on_init(self, context):
        try:
            if self.vars['unite_source_menu_compatibilty']:
                self.vars['menus'].update(
                    self.vim.vars['unite_source_menu_menus']
                )
        except KeyError:
            pass

    def gather_candidates(self, context):
        # If no menus have been defined, just exit
        if 'menus' not in self.vars or self.vars['menus'] == {}:
            return []

        lines = []
        menus = self.vars['menus']
        args = context['args']

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
                         'kind': 'jump_list',
                         'action__path': candidate[1],
                         }
                        for candidate in menus[menu]['file_candidates']
                    ])

                # Handle command candidates
                if 'command_candidates' in menus[menu]:
                    lines.extend([
                        {'word': str(candidate[0]),
                         'kind': 'command',
                         'action__command': candidate[1]
                         }
                        for candidate in menus[menu]['command_candidates']
                    ])
        else:
            # Display all the registered menus
            lines.extend([
                {'word': candidate,
                 'kind': 'command',
                 'action__command': 'Denite menu:' + candidate,
                 }
                for candidate in menus
            ])

        return lines
