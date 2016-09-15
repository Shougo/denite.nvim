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

    def on_init(self, context):
        # TODO: Could also check for unite_source_menu_menus?
        context['__menus'] = context['vars'].get('menus', {})

    def gather_candidates(self, context):
        lines = []

        menu_context = [option for option in context['sources']
                        if option['name'] == self.name][0]

        if menu_context == []:
            # Exit quickly
            return []

        # TODO: Get all the arguments,
        # in case some aren't passed directly to the menu
        if menu_context['args']:
            # TODO:  Check the menu name

            # Handle file candidates
            lines.extend([
                {'word': str(candidate[0]),
                 'action__path': candidate[1],
                 }
                for search_string in menu_context['args']
                for candidate
                in context['__menus'][search_string]['file_candidates']
            ])

            # TODO: Handle command candidates
            # TODO: Handle candidates
        else:
            # TODO: Display all the available menus
            lines.extend([{'word': candidate,
                           # TODO: Open the menu?
                           }
                          for candidate in context['__menus']
                          ]
                         )

        return lines
