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

        self.dict_key = '__menus'

    def on_init(self, context):
        context[self.dict_key] = context['custom']['source']['menu']['vars']\
            .get('menus', {})

        # TODO: Set a value to look for old unite menus from VIM?
        unite_menu_compatibilty = False
        if unite_menu_compatibilty:
            context[self.dict_key].update(
                self.vim.vars['unite_source_menu_menus']
            )

    def gather_candidates(self, context):
        # If no menus have been defined, just exit
        if self.dict_key not in context.keys() or not context[self.dict_key]:
            return []

        lines = []

        menu_args = context['args']

        if menu_args:
            # TODO:  Check the menu name

            # Handle file candidates
            lines.extend([
                {'word': str(candidate[0]),
                 'action__path': candidate[1],
                 }
                for search_string in menu_args
                for candidate
                in context[self.dict_key][search_string]['file_candidates']
            ])

            # TODO: Handle command candidates
            # TODO: Handle candidates
        else:
            # TODO: Display all the available menus
            lines.extend([{'word': candidate,
                           # TODO: Open the menu?
                           }
                          for candidate in context[self.dict_key]
                          ]
                         )

        return lines
