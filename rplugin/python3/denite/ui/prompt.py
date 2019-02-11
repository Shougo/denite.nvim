from .action import DEFAULT_ACTION_RULES
from datetime import timedelta, datetime
from ..prompt.prompt import (
    ACTION_KEYSTROKE_PATTERN,
    Prompt,
    STATUS_CANCEL,
)


class DenitePrompt(Prompt):
    def __init__(self, vim, context, denite):
        self.context = context
        super().__init__(vim)
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
        self.harvest_interval = 0.03
        self._previous_text = self.text
        self._timeout = datetime.now()

    def on_term(self, status):
        # NOTE:
        # 'inputrestore' is not required to be called while denite call it
        # at denite#start
        return status

    def on_update(self, status):
        if self.denite.is_async and self.denite.check_option():
            self.denite.quit()
            return STATUS_CANCEL
        return super().on_update(status)

    def on_harvest(self):
        # Set b:denite_context
        self.denite._bufvars['denite_context'] = self.context

        if self._timeout > datetime.now():
            return

        if not self.denite.is_async and self._previous_text == self.text:
            return

        if self.denite.update_candidates():
            self.denite.update_buffer()
        else:
            self.denite.update_status()

        if self._previous_text != self.text:
            self._previous_text = self.text
            self.denite.init_cursor()

        # NOTE
        # Redraw prompt to update the buffer.
        # Without 'redraw_prompt', the buffer is not updated often enough
        # for 'async' source.
        self.redraw_prompt()

    def on_keypress(self, keystroke):
        self._timeout = datetime.now() + timedelta(
            milliseconds=int(self.context['updatetime'])
        )

        m = ACTION_KEYSTROKE_PATTERN.match(str(keystroke))
        if m:
            ret = self.action.call(self, m.group('action'))
            bufvars = self.denite._bufvars
            if ('denite_new_context' in bufvars
                    and bufvars['denite_new_context']):
                # Update context
                self.context.update(bufvars['denite_new_context'])
                bufvars['denite_new_context'] = {}
                self.denite.redraw()
            return ret
        elif self.denite.current_mode == 'insert':
            # Updating text from a keystroke is a feature of 'insert' mode
            self.update_text(str(keystroke))
