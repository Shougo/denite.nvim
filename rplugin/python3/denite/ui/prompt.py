from .action import DEFAULT_ACTION_RULES
from ..prompt.prompt import (
    Prompt,
    STATUS_CANCEL,
)


DENITE_MODE_INSERT = 'insert'
DENITE_MODE_NORMAL = 'normal'


class DenitePrompt(Prompt):
    def __init__(self, vim, context, denite):
        self.context = context
        super().__init__(vim)
        self.__previous_text = self.text
        self.denite = denite
        self.action.register_from_rules(DEFAULT_ACTION_RULES)
        # Remove prompt:accept/prompt:cancel which would break denite
        self.action.unregister('prompt:accept')
        self.action.unregister('prompt:cancel')

    @property
    def text(self):
        return self.context.get('input', '')

    @text.setter
    def text(self, value):
        self.context['input'] = value

    @property
    def prefix(self):
        return '%s ' % self.context.get('prompt', '#')

    @property
    def highlight_prefix(self):
        return self.context.get('prompt_highlight', 'Statement')

    @property
    def highlight_text(self):
        return 'Normal'

    @property
    def highlight_cursor(self):
        return self.context.get('cursor_highlight', 'Cursor')

    def update_text(self, text):
        # DO NOT UPDATE text when the mode is not INSERT mode.
        if self.denite.current_mode == DENITE_MODE_INSERT:
            super().update_text(text)

    def on_update(self, status):
        if self.__previous_text != self.text:
            self.__previous_text = self.text
            self.denite.update_candidates()
            self.denite.update_buffer()
            self.denite.init_cursor()

        if self.denite.is_async and self.denite.check_empty():
            self.denite.quit()
            return STATUS_CANCEL
        return super().on_update(status)

    def on_harvest(self):
        if self.denite.is_async:
            self.denite.update_candidates()
            self.denite.update_buffer()
