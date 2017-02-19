from datetime import timedelta, datetime
from .action import DEFAULT_ACTION_RULES
from ..prompt.prompt import (
    ACTION_KEYSTROKE_PATTERN,
    Prompt,
    STATUS_CANCEL,
)


class DenitePrompt(Prompt):
    def __init__(self, vim, context, denite):
        self.context = context
        super().__init__(vim)
        self.__previous_text = self.text
        self.__timeout = None
        self.__timeoutlen = None
        self.__input = ''
        self.denite = denite
        self.action.register_from_rules(DEFAULT_ACTION_RULES)
        # Remove prompt:accept/prompt:cancel which would break denite
        self.action.unregister('prompt:accept', fail_silently=True)
        self.action.unregister('prompt:cancel', fail_silently=True)

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
        return self.context.get('highlight_cursor', 'Cursor')

    def on_init(self):
        # NOTE:
        # 'inputsave' is not required to be called while denite call it
        # at denite#start
        pass

    def on_term(self, status):
        # NOTE:
        # 'inputrestore' is not required to be called while denite call it
        # at denite#start
        return status

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
        if not self.denite.is_async or (
                self.__input != self.context['input'] and
                self.__timeout and datetime.now() < self.__timeout):
            return

        if self.denite.update_candidates():
            if self.context['reversed']:
                self.denite.init_cursor()
            self.denite.update_buffer()
        else:
            self.denite.update_status()

        # NOTE
        # Redraw prompt to update the buffer.
        # Without 'redraw_prompt', the buffer is not updated often enough
        # for 'async' source.
        self.redraw_prompt()

        self.__input = self.context['input']
        self.__timeout = datetime.now() + timedelta(
            milliseconds=int(self.context['timeoutlen']))

    def on_keypress(self, keystroke):
        m = ACTION_KEYSTROKE_PATTERN.match(str(keystroke))
        if m:
            return self.action.call(self, m.group('action'))
        elif self.denite.current_mode == 'insert':
            # Updating text from a keystroke is a feature of 'insert' mode
            self.update_text(str(keystroke))
