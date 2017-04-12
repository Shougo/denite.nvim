"""Prompt module."""
import copy
import re
import weakref
from collections import namedtuple
from datetime import timedelta
from .action import ACTION_PATTERN
from .util import build_echon_expr


ACTION_KEYSTROKE_PATTERN = re.compile(
    r'<(?P<action>%s)>' % ACTION_PATTERN.pattern
)


STATUS_PROGRESS = 0
STATUS_ACCEPT = 1
STATUS_CANCEL = 2
STATUS_INTERRUPT = 3

INSERT_MODE_INSERT = 1
INSERT_MODE_REPLACE = 2


Condition = namedtuple('Condition', ['text', 'caret_locus'])


class Prompt:
    """Prompt class."""

    prefix = ''

    highlight_prefix = 'Question'

    highlight_text = 'None'

    highlight_caret = 'IncSearch'

    def __init__(self, nvim):
        """Constructor.

        Args:
            nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
        """
        from .caret import Caret
        from .history import History
        from .keymap import DEFAULT_KEYMAP_RULES, Keymap
        from .action import DEFAULT_ACTION
        self.text = ''
        self.nvim = nvim
        self.insert_mode = INSERT_MODE_INSERT
        self.caret = Caret(weakref.proxy(self))
        self.history = History(weakref.proxy(self))
        self.action = copy.copy(DEFAULT_ACTION)
        self.keymap = Keymap.from_rules(nvim, DEFAULT_KEYMAP_RULES)
        # MacVim (GUI) has a problem on 'redraw'
        self.is_macvim = (
            nvim.call('has', 'gui_running') and nvim.call('has', 'mac')
        )

    def insert_text(self, text):
        """Insert text after the caret.

        Args:
            text (str): A text which will be inserted after the caret.

        Example:
            >>> from unittest.mock import MagicMock
            >>> nvim = MagicMock()
            >>> nvim.options = {'encoding': 'utf-8'}
            >>> prompt = Prompt(nvim)
            >>> prompt.text = "Hello Goodbye"
            >>> prompt.caret.locus = 3
            >>> prompt.insert_text('AA')
            >>> prompt.text
            'HelAAlo Goodbye'
        """
        locus = self.caret.locus
        self.text = ''.join([
            self.caret.get_backward_text(),
            text,
            self.caret.get_selected_text(),
            self.caret.get_forward_text(),
        ])
        self.caret.locus = locus + len(text)

    def replace_text(self, text):
        """Replace text after the caret.

        Args:
            text (str): A text which will be replaced after the caret.

        Example:
            >>> from unittest.mock import MagicMock
            >>> nvim = MagicMock()
            >>> nvim.options = {'encoding': 'utf-8'}
            >>> prompt = Prompt(nvim)
            >>> prompt.text = "Hello Goodbye"
            >>> prompt.caret.locus = 3
            >>> prompt.replace_text('AA')
            >>> prompt.text
            'HelAA Goodbye'
        """
        locus = self.caret.locus
        self.text = ''.join([
            self.caret.get_backward_text(),
            text,
            self.caret.get_forward_text()[len(text) - 1:],
        ])
        self.caret.locus = locus + len(text)

    def update_text(self, text):
        """Insert or replace text after the caret.

        Args:
            text (str): A text which will be replaced after the caret.

        Example:
            >>> from unittest.mock import MagicMock
            >>> nvim = MagicMock()
            >>> nvim.options = {'encoding': 'utf-8'}
            >>> prompt = Prompt(nvim)
            >>> prompt.text = "Hello Goodbye"
            >>> prompt.caret.locus = 3
            >>> prompt.insert_mode = INSERT_MODE_INSERT
            >>> prompt.update_text('AA')
            >>> prompt.text
            'HelAAlo Goodbye'
            >>> prompt.insert_mode = INSERT_MODE_REPLACE
            >>> prompt.update_text('BB')
            >>> prompt.text
            'HelAABB Goodbye'
        """
        if self.insert_mode == INSERT_MODE_INSERT:
            self.insert_text(text)
        else:
            self.replace_text(text)

    def redraw_prompt(self):
        """Redraw prompt."""
        # NOTE:
        # There is a highlight name 'Cursor' but some sometime the visibility
        # is quite low (e.g. tender) so use 'IncSearch' instead while the
        # visibility is quite good and most recent colorscheme care about it.
        backward_text = self.caret.get_backward_text()
        selected_text = self.caret.get_selected_text()
        forward_text = self.caret.get_forward_text()
        self.nvim.command('|'.join([
            'redraw',
            build_echon_expr(self.prefix, self.highlight_prefix),
            build_echon_expr(backward_text, self.highlight_text),
            build_echon_expr(selected_text, self.highlight_caret),
            build_echon_expr(forward_text, self.highlight_text),
        ]))
        if self.is_macvim:
            # MacVim requires extra 'redraw'
            self.nvim.command('redraw')

    def start(self):
        """Start prompt and return value.

        Returns:
            int: The status of the prompt.
        """
        status = self.on_init() or STATUS_PROGRESS
        if self.nvim.options['timeout']:
            timeoutlen = timedelta(
                milliseconds=int(self.nvim.options['timeoutlen'])
            )
        else:
            timeoutlen = None
        try:
            status = self.on_update(status) or STATUS_PROGRESS
            while status is STATUS_PROGRESS:
                self.on_redraw()
                status = self.on_keypress(self.keymap.harvest(
                    self.nvim,
                    timeoutlen=timeoutlen,
                    callback=self.on_harvest,
                )) or STATUS_PROGRESS
                status = self.on_update(status) or status
        except self.nvim.error as e:
            # NOTE:
            # neovim raise nvim.error instead of KeyboardInterrupt when Ctrl-C
            # has pressed so treat it as a real KeyboardInterrupt exception.
            if str(e) == "b'Keyboard interrupt'":
                status = STATUS_INTERRUPT
            else:
                raise e
        except KeyboardInterrupt:
            status = STATUS_INTERRUPT
        if self.text:
            self.nvim.call('histadd', 'input', self.text)
        return self.on_term(status)

    def on_init(self):
        """Initialize the prompt.

        It calls 'inputsave' function in Vim in default.

        Returns:
            None or int: The return value will be used as a status of the
                prompt mainloop, indicating that if return value is not
                STATUS_PROGRESS, the prompt mainloop immediately terminated.
                Returning None is equal to returning STATUS_PROGRESS.
        """
        self.nvim.call('inputsave')

    def on_update(self, status):
        """Update the prompt status and return the status.

        It is used to update the prompt status. In default, it does nothing and
        return the specified ``status`` directly.

        Args:
            status (int): A prompt status which is updated by previous
                on_keypress call.

        Returns:
            None or int: The return value will be used as a status of the
                prompt mainloop, indicating that if return value is not
                STATUS_PROGRESS, the prompt mainloop immediately terminated.
                Returning None is equal to returning STATUS_PROGRESS.
        """
        pass

    def on_redraw(self):
        """Redraw the prompt.

        It is used to redraw the prompt. In default, it echos specified prefix
        the caret, and input text.
        """
        self.redraw_prompt()

    def on_harvest(self):
        """Callback which is called during a keycode harvest.

        This callback is called most often. Developers should not call heavy
        procession on this callback.

        """
        pass

    def on_keypress(self, keystroke):
        """Handle a pressed keystroke and return the status.

        It is used to handle a pressed keystroke. Note that subclass should NOT
        override this method to perform actions. Register a new custom action
        instead. In default, it call action and return the result if the
        keystroke looks like <xxx:xxx>.

        Args:
            keystroke (Keystroke): A pressed keystroke instance. Note that this
                instance is a reslved keystroke instace by keymap.

        Returns:
            None or int: The return value will be used as a status of the
                prompt mainloop, indicating that if return value is not
                STATUS_PROGRESS, the prompt mainloop immediately terminated.
                Returning None is equal to returning STATUS_PROGRESS.
        """
        m = ACTION_KEYSTROKE_PATTERN.match(str(keystroke))
        if m:
            return self.action.call(self, m.group('action'))
        else:
            self.update_text(str(keystroke))

    def on_term(self, status):
        """Finalize the prompt.

        It calls 'inputrestore' function in Vim to finalize the prompt in
        default. The return value is used as a return value of the prompt.

        Args:
            status (int): A prompt status.

        Returns:
            int: A status which is used as a result value of the prompt.
        """
        self.nvim.call('inputrestore')
        return status

    def store(self):
        """Save current prompt condition into a Condition instance."""
        return Condition(
            text=self.text,
            caret_locus=self.caret.locus,
        )

    def restore(self, condition):
        """Load current prompt condition from a Condition instance."""
        self.text = condition.text
        self.caret.locus = condition.caret_locus
