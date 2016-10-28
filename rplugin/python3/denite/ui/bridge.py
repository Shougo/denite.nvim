import weakref
from .default import Default
from ..prompt.prompt import Prompt
from ..prompt.context import Context


class Bridge(Default):
    def __init__(self, vim):
        super().__init__(vim)
        self.__prompt = BridgePrompt(vim, weakref.proxy(self))

    def input_loop(self):
        self.__prompt.start()


class BridgeContext(Context):
    __slots__ = ('caret_locus', '_context')

    def __init__(self, context):
        self._context = context
        self.caret_locus = 0

    @property
    def text(self):
        return self._context.get('input', '')

    @text.setter
    def text(self, value):
        self._context['input'] = value


class BridgePrompt(Prompt):

    def __init__(self, vim, bridge):
        self.bridge = bridge
        super().__init__(vim, BridgeContext(bridge.context))

    def on_init(self, default):
        self.context._context = self.bridge.context
        self.bridge.init_buffer()

    def on_update(self, status):
        self.bridge.update_buffer()
        return status

    def on_redraw(self):
        return super().on_redraw()

    def on_keypress(self, keystroke):
        return super().on_keypress(keystroke)

    def on_term(self, status):
        self.bridge.quit()
        return status
