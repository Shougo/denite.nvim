"""Prompt module."""
import re
import copy
from datetime import timedelta

ACTION_KEYSTROKE_PATTERN = re.compile(r'<(\w+:\w+)>')

ESCAPE_ECHO = str.maketrans({
    '"': '\\"',
    '\\': '\\\\',
})

IMPRINTABLE_REPRESENTS = {
    '\a': '^G',
    '\b': '^H',             # NOTE: Neovim: <BS>, Vim: ^H. Follow Vim.
    '\t': '^I',
    '\n': '^J',
    '\v': '^K',
    '\f': '^L',
    '\r': '^M',
    '\udc80\udcffX': '^@',  # NOTE: ^0 representation in Vim.
}

IMPRINTABLE_PATTERN = re.compile(r'(%s)' % '|'.join(
    IMPRINTABLE_REPRESENTS.keys()
))


STATUS_PROGRESS = 0
STATUS_ACCEPT = 1
STATUS_CANCEL = 2
STATUS_ERROR = 3

INSERT_MODE_INSERT = 1
INSERT_MODE_REPLACE = 2


class Prompt:
    """Prompt class."""

    prefix = ''

    def __init__(self, nvim, context):
        """Constructor.

        Args:
            nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
            context (Context): A ``prompt.context.Context`` instance.
        """
        from .caret import Caret
        from .history import History
        from .keymap import DEFAULT_KEYMAP_RULES, Keymap
        from .action import DEFAULT_ACTION
        self.nvim = nvim
        self.insert_mode = INSERT_MODE_INSERT
        self.context = context
        self.caret = Caret(context)
        self.history = History(self)
        self.action = copy.copy(DEFAULT_ACTION)
        self.keymap = Keymap.from_rules(nvim, DEFAULT_KEYMAP_RULES)

    @property
    def text(self):
        """str: A current context text.

        It automatically adjust the current caret locus to the tail of the text
        if any text is assigned.

        It calls the following overridable methods in order of the appearance.

        - on_init - Only once
        - on_update
        - on_redraw
        - on_keypress
        - on_term - Only once

        Example:
            >>> from .context import Context
            >>> from unittest.mock import MagicMock
            >>> nvim = MagicMock()
            >>> nvim.options = {'encoding': 'utf-8'}
            >>> context = Context()
            >>> context.text = "Hello"
            >>> context.caret_locus = 3
            >>> prompt = Prompt(nvim, context)
            >>> prompt.text
            'Hello'
            >>> prompt.caret.locus
            3
            >>> prompt.text = "FooFooFoo"
            >>> prompt.text
            'FooFooFoo'
            >>> prompt.caret.locus
            9
        """
        return self.context.text

    @text.setter
    def text(self, value):
        self.context.text = value
        self.caret.locus = len(value)

    def apply_custom_mappings_from_vim_variable(self, varname):
        """Apply custom key mappings from Vim variable.

        Args:
            varname (str): A global Vim's variable name
        """
        if varname in self.nvim.vars:
            custom_mappings = self.nvim.vars[varname]
            for rule in custom_mappings:
                self.keymap.register_from_rule(self.nvim, rule)

    def insert_text(self, text):
        """Insert text after the caret.

        Args:
            text (str): A text which will be inserted after the caret.

        Example:
            >>> from .context import Context
            >>> from unittest.mock import MagicMock
            >>> nvim = MagicMock()
            >>> nvim.options = {'encoding': 'utf-8'}
            >>> context = Context()
            >>> context.text = "Hello Goodbye"
            >>> context.caret_locus = 3
            >>> prompt = Prompt(nvim, context)
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
            >>> from .context import Context
            >>> from unittest.mock import MagicMock
            >>> nvim = MagicMock()
            >>> nvim.options = {'encoding': 'utf-8'}
            >>> context = Context()
            >>> context.text = "Hello Goodbye"
            >>> context.caret_locus = 3
            >>> prompt = Prompt(nvim, context)
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
            >>> from .context import Context
            >>> from unittest.mock import MagicMock
            >>> nvim = MagicMock()
            >>> nvim.options = {'encoding': 'utf-8'}
            >>> context = Context()
            >>> context.text = "Hello Goodbye"
            >>> context.caret_locus = 3
            >>> prompt = Prompt(nvim, context)
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
        # NOTE:
        # There is a highlight name 'Cursor' but some sometime the visibility
        # is quite low (e.g. tender) so use 'IncSearch' instead while the
        # visibility is quite good and most recent colorscheme care about it.
        backward_text = self.caret.get_backward_text()
        selected_text = self.caret.get_selected_text()
        forward_text = self.caret.get_forward_text()
        self.nvim.command('|'.join([
            'redraw',
            _build_echon_expr('Question', self.prefix),
            _build_echon_expr('None', backward_text),
            _build_echon_expr('IncSearch', selected_text),
            _build_echon_expr('None', forward_text),
        ]))

    def start(self, default=None):
        """Start prompt with ``default`` text and return value.

        Args:
            default (None or str): A default text of the prompt. If omitted, a
                text in the context specified in the constructor is used.

        Returns:
            int: The status of the prompt.
        """
        status = self.on_init(default) or STATUS_PROGRESS
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
                status = self.on_keypress(
                    self.keymap.harvest(self.nvim, timeoutlen)
                ) or STATUS_PROGRESS
                status = self.on_update(status) or STATUS_PROGRESS
        except KeyboardInterrupt:
            status = STATUS_CANCEL
        except self.nvim.error as e:
            self.nvim.command('|'.join([
                'echoerr "%s"' % line.translate(ESCAPE_ECHO)
                for line in str(e).splitlines()
            ]))
            status = STATUS_ERROR
        self.nvim.command('redraw!')
        if self.text:
            self.nvim.call('histadd', 'input', self.text)
        return self.on_term(status)

    def on_init(self, default):
        """Initialize the prompt.

        It calls 'inputsave' function in Vim and assign ``default`` text to the
        ``self.text`` to initialize the prompt text in default.

        Args:
            default (None or str): A default text of the prompt. If omitted, a
                text in the context specified in the constructor is used.

        Returns:
            None or int: The return value will be used as a status of the
                prompt mainloop, indicating that if return value is not
                STATUS_PROGRESS, the prompt mainloop immediately terminated.
                Returning None is equal to returning STATUS_PROGRESS.
        """
        self.nvim.call('inputsave')
        if default:
            self.text = default

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
        return status

    def on_redraw(self):
        """Redraw the prompt.

        It is used to redraw the prompt. In default, it echos specified prefix
        the caret, and input text.
        """
        self.redraw_prompt()

    def on_keypress(self, keystroke):
        """Handle a pressed keystroke and return the status.

        It is used to handle a pressed keystroke. Note that subclass should NOT
        override this method to perform actions. Register a new custom action
        instead. In default, it call action and return the result if the
        keystroke is <xxx:xxx>or call Vim function XXX and return the result
        if the keystroke is <call:XXX>.

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
            return self.action.call(self, m.group(1))
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


def _build_echon_expr(hl, text):
    if not IMPRINTABLE_PATTERN.search(text):
        return 'echohl %s|echon "%s"' % (
            hl, text.translate(ESCAPE_ECHO)
        )
    p = 'echohl %s|echon "%%s"' % hl
    i = 'echohl %s|echon "%%s"' % ('SpecialKey' if hl == 'None' else hl)
    return '|'.join(
        p % term if index % 2 == 0 else i % IMPRINTABLE_REPRESENTS[term]
        for index, term in enumerate(IMPRINTABLE_PATTERN.split(text))
    )
