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
            'menus': {}
        }

    def on_init(self, context):
        # TODO: Set a value to look for old unite menus from VIM?
        unite_menu_compatibilty = False
        if unite_menu_compatibilty:
            self.vars['menus'].update(
                self.vim.vars['unite_source_menu_menus']
            )

    def gather_candidates(self, context):
        # If no menus have been defined, just exit
        if 'menus' not in self.vars.keys() or self.vars['menus'] == {}:
            return []

        lines = []
        menus = self.vars['menus']
        args = context['args']

        if args:
            # Loop through each menu option
            for menu in args:
                # If a menu doesn't exist, just continue gracefully
                # TODO: Print an error letting the user know
                if menu not in menus.keys():
                    continue

                # Handle file candidates
                if 'file_candidates' in menus[menu]:
                    lines.extend([
                        {'word': str(candidate[0]),
                         'action__path': candidate[1],
                         }
                        for candidate in menus[menu]['file_candidates']
                    ])

                # TODO: Handle command candidates
                # TODO: Handle candidates
        else:
            # TODO: Display all the available menus
            lines.extend([
                {'word': candidate,
                 # TODO: Open the menu?
                 }
                for candidate in menus
            ])

        return lines
