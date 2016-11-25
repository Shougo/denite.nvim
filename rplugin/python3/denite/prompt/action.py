"""Prompt action module."""
import re
from .digraph import Digraph
from .util import getchar, int2char, int2repr


ACTION_PATTERN = re.compile(
    r'(?P<name>(?:\w+):(?P<label>\w+))(?::(?P<params>.+))?'
)
"""Action name pattern."""


class Action:
    """Action class which hold action callbacks.

    Note:
        This class defines ``__slots__`` attribute so sub-class must override
        the attribute to extend available attributes.

    Attributes:
        registry (dict): An action dictionary.
    """

    __slots__ = ('registry',)

    def __init__(self):
        """Constructor."""
        self.registry = {}

    def clear(self):
        """Clear registered actions."""
        self.registry.clear()

    def register(self, name, callback):
        """Register action callback to a specified name.

        Args:
            name (str): An action name which follow
                {namespace}:{action name}:{params}
            callback (Callable[Prompt, str]): An action callback which take a
                ``prompt.prompt.Prompt`` instance, str and return None or int.

        Example:
            >>> from .prompt import STATUS_ACCEPT
            >>> action = Action()
            >>> action.register(
            ...     'prompt:accept', lambda prompt, params: STATUS_ACCEPT
            ... )
        """
        self.registry[name] = callback

    def register_from_rules(self, rules) -> None:
        """Register action callbacks from rules.

        Args:
            rules (Iterable): An iterator which returns rules. A rule is a
                (name, callback) tuple.

        Example:
            >>> from .prompt import STATUS_ACCEPT, STATUS_CANCEL
            >>> action = Action()
            >>> action.register_from_rules([
            ...     ('prompt:accept', lambda prompt, params: STATUS_ACCEPT),
            ...     ('prompt:cancel', lambda prompt, params: STATUS_CANCEL),
            ... ])
        """
        for rule in rules:
            self.register(*rule)

    def call(self, prompt, action):
        """Call a callback of specified action.

        Args:
            prompt (Prompt): A ``prompt.prompt.Prompt`` instance.
            name (str): An action name.

        Example:
            >>> from unittest.mock import MagicMock
            >>> from .prompt import STATUS_ACCEPT, STATUS_CANCEL
            >>> prompt = MagicMock()
            >>> action = Action()
            >>> action.register_from_rules([
            ...     ('prompt:accept', lambda prompt, params: STATUS_ACCEPT),
            ...     ('prompt:cancel', lambda prompt, params: STATUS_CANCEL),
            ...     ('prompt:do', lambda prompt, params: params),
            ... ])
            >>> action.call(prompt, 'prompt:accept')
            1
            >>> action.call(prompt, 'prompt:cancel')
            2
            >>> action.call(prompt, 'prompt:do:foo')
            'foo'
            >>> action.call(prompt, 'unknown:accept')
            1
            >>> action.call(prompt, 'unknown:unknown')
            Traceback (most recent call last):
              ...
            AttributeError: No action "unknown:unknown" has registered.

        Returns:
            None or int: None or int which represent the prompt status.
        """
        m = ACTION_PATTERN.match(action)
        name = m.group('name')
        label = m.group('label')
        params = m.group('params') or ''
        alternative_name = 'prompt:' + label
        # fallback to the prompt's builtin action if no name found in registry
        if name not in self.registry and alternative_name in self.registry:
            name = alternative_name
        # Execute action or raise AttributeError
        if name in self.registry:
            fn = self.registry[name]
            return fn(prompt, params)
        raise AttributeError(
            'No action "%s" has registered.' % name
        )

    @classmethod
    def from_rules(cls, rules):
        """Create a new action instance from rules.

        Args:
            rules (Iterable): An iterator which returns rules. A rule is a
                (name, callback) tuple.

        Example:
            >>> from .prompt import STATUS_ACCEPT, STATUS_CANCEL
            >>> Action.from_rules([
            ...     ('prompt:accept', lambda prompt, params: STATUS_ACCEPT),
            ...     ('prompt:cancel', lambda prompt, params: STATUS_CANCEL),
            ... ])
            <....action.Action object at ...>

        Returns:
            Action: An action instance.
        """
        action = cls()
        action.register_from_rules(rules)
        return action


# Default actions -------------------------------------------------------------
def _accept(prompt, params):
    from .prompt import STATUS_ACCEPT
    return STATUS_ACCEPT


def _cancel(prompt, params):
    from .prompt import STATUS_CANCEL
    return STATUS_CANCEL


def _toggle_insert_mode(prompt, params):
    from .prompt import INSERT_MODE_INSERT, INSERT_MODE_REPLACE
    if prompt.insert_mode == INSERT_MODE_INSERT:
        prompt.insert_mode = INSERT_MODE_REPLACE
    else:
        prompt.insert_mode = INSERT_MODE_INSERT


def _delete_char_before_caret(prompt, params):
    if prompt.caret.locus == 0:
        return
    prompt.text = ''.join([
        prompt.caret.get_backward_text()[:-1],
        prompt.caret.get_selected_text(),
        prompt.caret.get_forward_text(),
    ])
    prompt.caret.locus -= 1


def _delete_word_before_caret(prompt, params):
    if prompt.caret.locus == 0:
        return
    # Use vim's substitute to respect 'iskeyword'
    original_backward_text = prompt.caret.get_backward_text()
    backward_text = prompt.nvim.call(
        'substitute',
        original_backward_text, '\k\+\s*$', '', '',
    )
    prompt.text = ''.join([
        backward_text,
        prompt.caret.get_selected_text(),
        prompt.caret.get_forward_text(),
    ])
    prompt.caret.locus -= len(original_backward_text) - len(backward_text)


def _delete_char_under_caret(prompt, params):
    prompt.text = ''.join([
        prompt.caret.get_backward_text(),
        prompt.caret.get_forward_text(),
    ])


def _delete_text_after_caret(prompt, params):
    prompt.text = prompt.caret.get_backward_text()
    prompt.caret.locus = prompt.caret.tail


def _delete_entire_text(prompt, params):
    prompt.text = ''
    prompt.caret.locus = 0


def _move_caret_to_left(prompt, params):
    prompt.caret.locus -= 1


def _move_caret_to_one_word_left(prompt, params):
    # Use vim's substitute to respect 'iskeyword'
    original_text = prompt.caret.get_backward_text()
    substituted_text = prompt.nvim.call(
        'substitute',
        original_text, '\k\+\s\?$', '', '',
    )
    offset = len(original_text) - len(substituted_text)
    prompt.caret.locus -= 1 if not offset else offset


def _move_caret_to_right(prompt, params):
    prompt.caret.locus += 1


def _move_caret_to_one_word_right(prompt, params):
    # Use vim's substitute to respect 'iskeyword'
    original_text = prompt.caret.get_forward_text()
    substituted_text = prompt.nvim.call(
        'substitute',
        original_text, '^\k\+', '', '',
    )
    prompt.caret.locus += 1 + len(original_text) - len(substituted_text)


def _move_caret_to_head(prompt, params):
    prompt.caret.locus = prompt.caret.head


def _move_caret_to_lead(prompt, params):
    prompt.caret.locus = prompt.caret.lead


def _move_caret_to_tail(prompt, params):
    prompt.caret.locus = prompt.caret.tail


def _assign_previous_text(prompt, params):
    prompt.text = prompt.history.previous()
    prompt.caret.locus = prompt.caret.tail


def _assign_next_text(prompt, params):
    prompt.text = prompt.history.next()
    prompt.caret.locus = prompt.caret.tail


def _assign_previous_matched_text(prompt, params):
    prompt.text = prompt.history.previous_match()
    prompt.caret.locus = prompt.caret.tail


def _assign_next_matched_text(prompt, params):
    prompt.text = prompt.history.next_match()
    prompt.caret.locus = prompt.caret.tail


def _paste_from_register(prompt, params):
    state = prompt.store()
    prompt.update_text('"')
    prompt.redraw_prompt()
    reg = int2char(prompt.nvim, getchar(prompt.nvim))
    prompt.restore(state)
    val = prompt.nvim.call('getreg', reg)
    prompt.update_text(val)


def _paste_from_default_register(prompt, params):
    val = prompt.nvim.call('getreg', prompt.nvim.vvars['register'])
    prompt.update_text(val)


def _yank_to_register(prompt, params):
    state = prompt.store()
    prompt.update_text("'")
    prompt.redraw_prompt()
    reg = int2char(prompt.nvim, getchar(prompt.nvim))
    prompt.restore(state)
    prompt.nvim.call('setreg', reg, prompt.text)


def _yank_to_default_register(prompt, params):
    prompt.nvim.call('setreg', prompt.nvim.vvars['register'], prompt.text)


def _insert_special(prompt, params):
    state = prompt.store()
    prompt.update_text('^')
    prompt.redraw_prompt()
    code = getchar(prompt.nvim)
    prompt.restore(state)
    # Substitute special keys into control char
    if code == b'\x80kb':
        code = 0x08  # ^H
    char = int2repr(prompt.nvim, code)
    prompt.update_text(char)


def _insert_digraph(prompt, params):
    state = prompt.store()
    prompt.update_text('?')
    prompt.redraw_prompt()
    digraph = Digraph()
    char = digraph.retrieve(prompt.nvim)
    prompt.restore(state)
    prompt.update_text(char)


DEFAULT_ACTION = Action.from_rules([
    ('prompt:accept', _accept),
    ('prompt:cancel', _cancel),
    ('prompt:toggle_insert_mode', _toggle_insert_mode),
    ('prompt:delete_char_before_caret', _delete_char_before_caret),
    ('prompt:delete_word_before_caret', _delete_word_before_caret),
    ('prompt:delete_char_under_caret', _delete_char_under_caret),
    ('prompt:delete_text_after_caret', _delete_text_after_caret),
    ('prompt:delete_entire_text', _delete_entire_text),
    ('prompt:move_caret_to_left', _move_caret_to_left),
    ('prompt:move_caret_to_one_word_left', _move_caret_to_one_word_left),
    ('prompt:move_caret_to_right', _move_caret_to_right),
    ('prompt:move_caret_to_one_word_right', _move_caret_to_one_word_right),
    ('prompt:move_caret_to_head', _move_caret_to_head),
    ('prompt:move_caret_to_lead', _move_caret_to_lead),
    ('prompt:move_caret_to_tail', _move_caret_to_tail),
    ('prompt:assign_previous_text', _assign_previous_text),
    ('prompt:assign_next_text', _assign_next_text),
    ('prompt:assign_previous_matched_text', _assign_previous_matched_text),
    ('prompt:assign_next_matched_text', _assign_next_matched_text),
    ('prompt:paste_from_register', _paste_from_register),
    ('prompt:paste_from_default_register', _paste_from_default_register),
    ('prompt:yank_to_register', _yank_to_register),
    ('prompt:yank_to_default_register', _yank_to_default_register),
    ('prompt:insert_special', _insert_special),
    ('prompt:insert_digraph', _insert_digraph),
])
