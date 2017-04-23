"""Keymap."""
import time
from collections import namedtuple
from datetime import datetime
from operator import itemgetter
from .key import Key
from .keystroke import Keystroke
from .util import getchar


DefinitionBase = namedtuple('DefinitionBase', [
    'lhs',
    'rhs',
    'noremap',
    'nowait',
    'expr',
])


class Definition(DefinitionBase):
    """An individual keymap definition."""

    __slots__ = ()

    def __new__(cls, lhs, rhs, noremap=False, nowait=False, expr=False):
        """Create a new instance of the definition."""
        if expr and not isinstance(rhs, str):
            raise AttributeError(
                '"rhs" of "expr" mapping requires to be a str.'
            )
        return super().__new__(cls, lhs, rhs, noremap, nowait, expr)

    @classmethod
    def parse(cls, nvim, rule):
        """Parse a rule (list) and return a definition instance."""
        if len(rule) == 2:
            lhs, rhs = rule
            flags = ''
        elif len(rule) == 3:
            lhs, rhs, flags = rule
        else:
            raise AttributeError(
                'To many arguments are specified.'
            )
        flags = flags.split()
        kwargs = {}
        for flag in flags:
            if flag not in ['noremap', 'nowait', 'expr']:
                raise AttributeError(
                    'Unknown flag "%s" has specified.' % flag
                )
            kwargs[flag] = True
        lhs = Keystroke.parse(nvim, lhs)
        if not kwargs.get('expr', False):
            rhs = Keystroke.parse(nvim, rhs)
        return cls(lhs, rhs, **kwargs)


class Keymap:
    """Keymap."""

    __slots__ = ('registry',)

    def __init__(self):
        """Constructor."""
        self.registry = {}

    def clear(self):
        """Clear registered keymaps."""
        self.registry.clear()

    def register(self, definition):
        """Register a keymap.

        Args:
            definition (Definition): A definition instance.

        Example:
            >>> from .keystroke import Keystroke
            >>> from unittest.mock import MagicMock
            >>> nvim = MagicMock()
            >>> nvim.options = {'encoding': 'utf-8'}
            >>> keymap = Keymap()
            >>> keymap.register(Definition(
            ...     Keystroke.parse(nvim, '<C-H>'),
            ...     Keystroke.parse(nvim, '<BS>'),
            ... ))
            >>> keymap.register(Definition(
            ...     Keystroke.parse(nvim, '<C-H>'),
            ...     Keystroke.parse(nvim, '<BS>'),
            ...     noremap=True,
            ... ))
            >>> keymap.register(Definition(
            ...     Keystroke.parse(nvim, '<C-H>'),
            ...     Keystroke.parse(nvim, '<BS>'),
            ...     nowait=True,
            ... ))
            >>> keymap.register(Definition(
            ...     Keystroke.parse(nvim, '<C-H>'),
            ...     Keystroke.parse(nvim, '<BS>'),
            ...     noremap=True,
            ...     nowait=True,
            ... ))

        """
        self.registry[definition.lhs] = definition

    def register_from_rule(self, nvim, rule):
        """Register a keymap from a rule.

        Args:
            nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
            rule (tuple): A rule tuple.

        Example:
            >>> from .keystroke import Keystroke
            >>> from unittest.mock import MagicMock
            >>> nvim = MagicMock()
            >>> nvim.options = {'encoding': 'utf-8'}
            >>> keymap = Keymap()
            >>> keymap.register_from_rule(nvim, ['<C-H>', '<BS>'])
            >>> keymap.register_from_rule(nvim, [
            ...     '<C-H>',
            ...     '<BS>',
            ...     'noremap',
            ... ])
            >>> keymap.register_from_rule(nvim, [
            ...     '<C-H>',
            ...     '<BS>',
            ...     'noremap nowait',
            ... ])

        """
        self.register(Definition.parse(nvim, rule))

    def register_from_rules(self, nvim, rules):
        """Register keymaps from raw rule tuple.

        Args:
            nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
            rules (tuple): A tuple of rules.

        Example:
            >>> from .keystroke import Keystroke
            >>> from unittest.mock import MagicMock
            >>> nvim = MagicMock()
            >>> nvim.options = {'encoding': 'utf-8'}
            >>> lhs1 = Keystroke.parse(nvim, '<C-H>')
            >>> lhs2 = Keystroke.parse(nvim, '<C-D>')
            >>> lhs3 = Keystroke.parse(nvim, '<C-M>')
            >>> rhs1 = Keystroke.parse(nvim, '<BS>')
            >>> rhs2 = Keystroke.parse(nvim, '<DEL>')
            >>> rhs3 = Keystroke.parse(nvim, '<CR>')
            >>> keymap = Keymap()
            >>> keymap.register_from_rules(nvim, [
            ...     (lhs1, rhs1),
            ...     (lhs2, rhs2, 'noremap'),
            ...     (lhs3, rhs3, 'nowait'),
            ... ])

        """
        for rule in rules:
            self.register_from_rule(nvim, rule)

    def filter(self, lhs):
        """Filter keymaps by ``lhs`` Keystroke and return a sorted candidates.

        Args:
            lhs (Keystroke): A left hand side Keystroke instance.

        Example:
            >>> from .keystroke import Keystroke
            >>> from unittest.mock import MagicMock
            >>> nvim = MagicMock()
            >>> nvim.options = {'encoding': 'utf-8'}
            >>> k = lambda x: Keystroke.parse(nvim, x)
            >>> keymap = Keymap()
            >>> keymap.register_from_rules(nvim, [
            ...     ('<C-A><C-A>', '<prompt:A>'),
            ...     ('<C-A><C-B>', '<prompt:B>'),
            ...     ('<C-B><C-A>', '<prompt:C>'),
            ... ])
            >>> candidates = keymap.filter(k(''))
            >>> len(candidates)
            3
            >>> candidates[0]
            Definition(..., rhs=(Key(code=b'<prompt:A>', ...)
            >>> candidates[1]
            Definition(..., rhs=(Key(code=b'<prompt:B>', ...)
            >>> candidates[2]
            Definition(..., rhs=(Key(code=b'<prompt:C>', ...)
            >>> candidates = keymap.filter(k('<C-A>'))
            >>> len(candidates)
            2
            >>> candidates[0]
            Definition(..., rhs=(Key(code=b'<prompt:A>', ...)
            >>> candidates[1]
            Definition(..., rhs=(Key(code=b'<prompt:B>', ...)
            >>> candidates = keymap.filter(k('<C-A><C-A>'))
            >>> len(candidates)
            1
            >>> candidates[0]
            Definition(..., rhs=(Key(code=b'<prompt:A>', ...)

        Returns:
            Iterator[Definition]: Sorted Definition instances which starts from
                `lhs` Keystroke instance
        """
        candidates = (
            self.registry[k]
            for k in self.registry.keys() if k.startswith(lhs)
        )
        return sorted(candidates, key=itemgetter(0))

    def resolve(self, nvim, lhs, nowait=False):
        """Resolve ``lhs`` Keystroke instance and return resolved keystroke.

        Args:
            nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
            lhs (Keystroke): A left hand side Keystroke instance.
            nowait (bool): Return a first exact matched keystroke even there
                are multiple keystroke instances are matched.

        Example:
            >>> from .keystroke import Keystroke
            >>> from unittest.mock import MagicMock
            >>> nvim = MagicMock()
            >>> nvim.options = {'encoding': 'utf-8'}
            >>> k = lambda x: Keystroke.parse(nvim, x)
            >>> keymap = Keymap()
            >>> keymap.register_from_rules(nvim, [
            ...     ('<C-A><C-A>', '<prompt:A>'),
            ...     ('<C-A><C-B>', '<prompt:B>'),
            ...     ('<C-B><C-A>', '<C-A><C-A>', ''),
            ...     ('<C-B><C-B>', '<C-A><C-B>', 'noremap'),
            ...     ('<C-C>', '<prompt:C>', ''),
            ...     ('<C-C><C-A>', '<prompt:C1>'),
            ...     ('<C-C><C-B>', '<prompt:C2>'),
            ...     ('<C-D>', '<prompt:D>', 'nowait'),
            ...     ('<C-D><C-A>', '<prompt:D1>'),
            ...     ('<C-D><C-B>', '<prompt:D2>'),
            ... ])
            >>> # No mapping starts from <C-C> so <C-C> is returned
            >>> keymap.resolve(nvim, k('<C-Z>'))
            (Key(code=26, ...),)
            >>> # No single keystroke is resolved in the following case so None
            >>> # will be returned.
            >>> keymap.resolve(nvim, k('')) is None
            True
            >>> keymap.resolve(nvim, k('<C-A>')) is None
            True
            >>> # A single keystroke is resolved so rhs is returned.
            >>> # will be returned.
            >>> keymap.resolve(nvim, k('<C-A><C-A>'))
            (Key(code=b'<prompt:A>', ...),)
            >>> keymap.resolve(nvim, k('<C-A><C-B>'))
            (Key(code=b'<prompt:B>', ...),)
            >>> # noremap = False so recursively resolved
            >>> keymap.resolve(nvim, k('<C-B><C-A>'))
            (Key(code=b'<prompt:A>', ...),)
            >>> # noremap = True so resolved only once
            >>> keymap.resolve(nvim, k('<C-B><C-B>'))
            (Key(code=1, ...), Key(code=2, ...))
            >>> # nowait = False so no single keystroke could be resolved.
            >>> keymap.resolve(nvim, k('<C-C>')) is None
            True
            >>> # nowait = True so the first matched candidate is returned.
            >>> keymap.resolve(nvim, k('<C-D>'))
            (Key(code=b'<prompt:D>', ...),)

        Returns:
            None or Keystroke: None if no single keystroke instance is
                resolved. Otherwise return a resolved keystroke instance or
                ``lhs`` itself if no mapping is available for ``lhs``
                keystroke.
        """
        candidates = list(self.filter(lhs))
        n = len(candidates)
        if n == 0:
            return lhs
        elif n == 1:
            definition = candidates[0]
            if definition.lhs == lhs:
                return self._resolve(nvim, definition)
        elif nowait:
            # Use the first matched candidate if lhs is equal
            definition = candidates[0]
            if definition.lhs == lhs:
                return self._resolve(nvim, definition)
        else:
            # Check if the current first candidate is defined as nowait
            definition = candidates[0]
            if definition.nowait and definition.lhs == lhs:
                return self._resolve(nvim, definition)
        return None

    def _resolve(self, nvim, definition):
        if definition.expr:
            rhs = Keystroke.parse(nvim, nvim.eval(definition.rhs))
        else:
            rhs = definition.rhs
        if definition.noremap:
            return rhs
        return self.resolve(nvim, rhs, nowait=True)

    def harvest(self, nvim, timeoutlen=None, callback=None):
        """Harvest a keystroke from getchar in Vim and return resolved.

        It reads 'timeout' and 'timeoutlen' options in Vim and harvest a
        keystroke as Vim does. For example, if there is a key mapping for
        <C-X><C-F>, it waits 'timeoutlen' milliseconds after user hit <C-X>.
        If user continue <C-F> within timeout, it returns <C-X><C-F>. Otherwise
        it returns <C-X> before user continue <C-F>.
        If 'timeout' options is 0, it wait the next hit forever.

        Note that it returns a key immediately if the key is not a part of the
        registered mappings.

        Args:
            nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
            timeoutlen (datetime.timedelta): A timedelta instance which
                indicate the timeout.
            callback (Callable): A callback function which is called every
                before the internal getchar() has called.

        Returns:
            Keystroke: A resolved keystroke.

        """
        previous = None
        while True:
            code = _getcode(
                nvim,
                datetime.now() + timeoutlen if timeoutlen else None,
                callback=callback,
            )
            if code is None and previous is None:
                # timeout without input
                continue
            elif code is None:
                # timeout
                return self.resolve(nvim, previous, nowait=True) or previous
            previous = Keystroke((previous or ()) + (Key.parse(nvim, code),))
            keystroke = self.resolve(nvim, previous, nowait=False)
            if keystroke:
                # resolved
                return keystroke

    @classmethod
    def from_rules(cls, nvim, rules):
        """Create a keymap instance from a rule tuple.

        Args:
            nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
            rules (tuple): A tuple of rules.

        Example:
            >>> from .keystroke import Keystroke
            >>> from unittest.mock import MagicMock
            >>> nvim = MagicMock()
            >>> nvim.options = {'encoding': 'utf-8'}
            >>> lhs1 = Keystroke.parse(nvim, '<C-H>')
            >>> lhs2 = Keystroke.parse(nvim, '<C-D>')
            >>> lhs3 = Keystroke.parse(nvim, '<C-M>')
            >>> rhs1 = Keystroke.parse(nvim, '<BS>')
            >>> rhs2 = Keystroke.parse(nvim, '<DEL>')
            >>> rhs3 = Keystroke.parse(nvim, '<CR>')
            >>> keymap = Keymap.from_rules(nvim, [
            ...     (lhs1, rhs1),
            ...     (lhs2, rhs2, 'noremap'),
            ...     (lhs3, rhs3, 'nowait'),
            ... ])

        Returns:
            Keymap: A keymap instance
        """
        keymap = cls()
        keymap.register_from_rules(nvim, rules)
        return keymap


def _getcode(nvim, timeout, callback=None, sleep=0.033):
    while not timeout or timeout > datetime.now():
        if callback:
            callback()
        code = getchar(nvim, False)
        if code != 0:
            return code
        time.sleep(sleep)
    return None


DEFAULT_KEYMAP_RULES = (
    ('<C-B>', '<prompt:move_caret_to_head>', 'noremap'),
    ('<C-E>', '<prompt:move_caret_to_tail>', 'noremap'),
    ('<BS>', '<prompt:delete_char_before_caret>', 'noremap'),
    ('<C-H>', '<prompt:delete_char_before_caret>', 'noremap'),
    ('<S-TAB>', '<prompt:assign_previous_text>', 'noremap'),
    ('<C-J>', '<prompt:accept>', 'noremap'),
    ('<C-K>', '<prompt:insert_digraph>', 'noremap'),
    ('<CR>', '<prompt:accept>', 'noremap'),
    ('<C-M>', '<prompt:accept>', 'noremap'),
    ('<C-N>', '<prompt:assign_next_text>', 'noremap'),
    ('<C-P>', '<prompt:assign_previous_text>', 'noremap'),
    ('<C-Q>', '<prompt:insert_special>', 'noremap'),
    ('<C-R>', '<prompt:paste_from_register>', 'noremap'),
    ('<C-U>', '<prompt:delete_entire_text>', 'noremap'),
    ('<C-V>', '<prompt:insert_special>', 'noremap'),
    ('<C-W>', '<prompt:delete_word_before_caret>', 'noremap'),
    ('<ESC>', '<prompt:cancel>', 'noremap'),
    ('<DEL>', '<prompt:delete_char_under_caret>', 'noremap'),
    ('<Left>', '<prompt:move_caret_to_left>', 'noremap'),
    ('<S-Left>', '<prompt:move_caret_to_one_word_left>', 'noremap'),
    ('<C-Left>', '<prompt:move_caret_to_one_word_left>', 'noremap'),
    ('<Right>', '<prompt:move_caret_to_right>', 'noremap'),
    ('<S-Right>', '<prompt:move_caret_to_one_word_right>', 'noremap'),
    ('<C-Right>', '<prompt:move_caret_to_one_word_right>', 'noremap'),
    ('<Up>', '<prompt:assign_previous_matched_text>', 'noremap'),
    ('<S-Up>', '<prompt:assign_previous_text>', 'noremap'),
    ('<Down>', '<prompt:assign_next_matched_text>', 'noremap'),
    ('<S-Down>', '<prompt:assign_next_text>', 'noremap'),
    ('<Home>', '<prompt:move_caret_to_head>', 'noremap'),
    ('<End>', '<prompt:move_caret_to_tail>', 'noremap'),
    ('<PageDown>', '<prompt:assign_next_text>', 'noremap'),
    ('<PageUp>', '<prompt:assign_previous_text>', 'noremap'),
    ('<INSERT>', '<prompt:toggle_insert_mode>', 'noremap'),
)
