"""Action module."""
import re
from .digraph import Digraph
from .util import int2char, int2repr, getchar


class Action:
    """Action class which holds action callbacks.

    Attributes:
        registry (dict): An action dictionary.
    """

    __slots__ = ('registry',)

    def __init__(self):
        """Constructor."""
        self.registry = {}

    def register(self, name, callback):
        """Register action callback to a specified name.

        Args:
            name (str): An action name which follow {namespace}:{action name}
            callback (Callable): An action callback which take a
                ``prompt.prompt.Prompt`` instance and return None or int.

        Example:
            >>> from .prompt import STATUS_ACCEPT
            >>> action = Action()
            >>> action.register('prompt:accept', lambda prompt: STATUS_ACCEPT)
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
            ...     ('prompt:accept', lambda prompt: STATUS_ACCEPT),
            ...     ('prompt:cancel', lambda prompt: STATUS_CANCEL),
            ... ])
        """
        for rule in rules:
            self.register(*rule)

    def call(self, prompt, name):
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
            ...     ('prompt:accept', lambda prompt: STATUS_ACCEPT),
            ...     ('prompt:cancel', lambda prompt: STATUS_CANCEL),
            ... ])
            >>> action.call(prompt, 'prompt:accept')
            1
            >>> action.call(prompt, 'unknown:accept')
            1
            >>> action.call(prompt, 'unknown:unknown')
            Traceback (most recent call last):
              ...
            AttributeError: No action "unknown:unknown" has registered.

        Returns:
            None or int: None or int which represent the prompt status.
        """
        alternative_name = re.sub(r'[^:]+:(.*)', r'prompt:\1', name)
        if name not in self.registry and alternative_name in self.registry:
            # fallback to the prompt's builtin action
            name = alternative_name
        if name in self.registry:
            fn = self.registry[name]
            return fn(prompt)
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
            ...     ('prompt:accept', lambda prompt: STATUS_ACCEPT),
            ...     ('prompt:cancel', lambda prompt: STATUS_CANCEL),
            ... ])
            <....action.Action object at ...>

        Returns:
            Action: An action instance.
        """
        action = cls()
        action.register_from_rules(rules)
        return action


# Default actions -------------------------------------------------------------
def _accept(prompt):
    from .prompt import STATUS_ACCEPT
    return STATUS_ACCEPT


def _cancel(prompt):
    from .prompt import STATUS_CANCEL
    return STATUS_CANCEL


def _toggle_insert_mode(prompt):
    from .prompt import INSERT_MODE_INSERT, INSERT_MODE_REPLACE
    if prompt.insert_mode == INSERT_MODE_INSERT:
        prompt.insert_mode = INSERT_MODE_REPLACE
    else:
        prompt.insert_mode = INSERT_MODE_INSERT


def _delete_char_before_caret(prompt):
    if prompt.caret.locus == 0:
        return
    prompt.context.text = ''.join([
        prompt.caret.get_backward_text()[:-1],
        prompt.caret.get_selected_text(),
        prompt.caret.get_forward_text(),
    ])
    prompt.caret.locus -= 1


def _delete_word_before_caret(prompt):
    if prompt.caret.locus == 0:
        return
    # Use vim's substitute to respect 'iskeyword'
    original_backward_text = prompt.caret.get_backward_text()
    backward_text = prompt.nvim.call(
        'substitute',
        original_backward_text, '\k\+\s*$', '', '',
    )
    prompt.context.text = ''.join([
        backward_text,
        prompt.caret.get_selected_text(),
        prompt.caret.get_forward_text(),
    ])
    prompt.caret.locus -= len(original_backward_text) - len(backward_text)


def _delete_char_under_caret(prompt):
    prompt.context.text = ''.join([
        prompt.caret.get_backward_text(),
        prompt.caret.get_forward_text(),
    ])


def _delete_text_after_caret(prompt):
    prompt.context.text = prompt.caret.get_backward_text()
    prompt.caret.locus = prompt.caret.tail


def _delete_entire_text(prompt):
    prompt.context.text = ''
    prompt.caret.locus = prompt.caret.tail


def _move_caret_to_left(prompt):
    prompt.caret.locus -= 1


def _move_caret_to_one_word_left(prompt):
    # Use vim's substitute to respect 'iskeyword'
    original_text = prompt.caret.get_backward_text()
    substituted_text = prompt.nvim.call(
        'substitute',
        original_text, '\k\+\s\?$', '', '',
    )
    offset = len(original_text) - len(substituted_text)
    prompt.caret.locus -= 1 if not offset else offset


def _move_caret_to_right(prompt):
    prompt.caret.locus += 1


def _move_caret_to_one_word_right(prompt):
    # Use vim's substitute to respect 'iskeyword'
    original_text = prompt.caret.get_forward_text()
    substituted_text = prompt.nvim.call(
        'substitute',
        original_text, '^\k\+', '', '',
    )
    prompt.caret.locus += 1 + len(original_text) - len(substituted_text)


def _move_caret_to_head(prompt):
    prompt.caret.locus = prompt.caret.head


def _move_caret_to_lead(prompt):
    prompt.caret.locus = prompt.caret.lead


def _move_caret_to_tail(prompt):
    prompt.caret.locus = prompt.caret.tail


def _assign_previous_text(prompt):
    prompt.text = prompt.history.previous()


def _assign_next_text(prompt):
    prompt.text = prompt.history.next()


def _assign_previous_matched_text(prompt):
    prompt.text = prompt.history.previous_match()


def _assign_next_matched_text(prompt):
    prompt.text = prompt.history.next_match()


def _paste_from_register(prompt):
    context = prompt.context.to_dict()
    prompt.update_text('"')
    prompt.redraw_prompt()
    reg = int2char(prompt.nvim, getchar(prompt.nvim))
    prompt.context.extend(context)
    val = prompt.nvim.call('getreg', reg)
    prompt.update_text(val)


def _paste_from_default_register(prompt):
    val = prompt.nvim.call('getreg', prompt.nvim.vvars['register'])
    prompt.update_text(val)


def _yank_to_register(prompt):
    context = prompt.context.to_dict()
    prompt.update_text("'")
    prompt.redraw_prompt()
    reg = int2char(prompt.nvim, getchar(prompt.nvim))
    prompt.context.extend(context)
    prompt.nvim.call('setreg', reg, prompt.text)


def _yank_to_default_register(prompt):
    prompt.nvim.call('setreg', prompt.nvim.vvars['register'], prompt.text)


def _insert_special(prompt):
    context = prompt.context.to_dict()
    prompt.update_text('^')
    prompt.redraw_prompt()
    code = getchar(prompt.nvim)
    prompt.context.extend(context)
    # Substitute special keys into control char
    if code == b'\x80kb':
        code = 0x08  # ^H
    char = int2repr(prompt.nvim, code)
    prompt.update_text(char)


def _insert_digraph(prompt):
    context = prompt.context.to_dict()
    prompt.update_text('?')
    prompt.redraw_prompt()
    digraph = Digraph()
    char = digraph.retrieve(prompt.nvim)
    prompt.context.extend(context)
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
