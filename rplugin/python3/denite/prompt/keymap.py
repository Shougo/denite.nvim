"""Keymap."""
import time
from operator import itemgetter
from datetime import datetime
from .key import Key
from .keystroke import Keystroke
from .util import getchar


class Keymap:
    """Keymap."""

    __slots__ = ('registry',)

    def __init__(self):
        """Constructor."""
        self.registry = {}

    def register(self, lhs, rhs, noremap=False, nowait=False):
        """Register a keymap.

        Args:
            lhs (Keystroke): A left hand side Keystroke instance of the
                mapping.
            rhs (Keystroke): A right hand side Keystroke instance of the
                mapping.
            noremap (bool): A boolean to indicate noremap in Vim.
            nowait (bool): A boolean to indicate nowait in Vim.

        Example:
            >>> from .keystroke import Keystroke
            >>> from unittest.mock import MagicMock
            >>> nvim = MagicMock()
            >>> nvim.options = {'encoding': 'utf-8'}
            >>> keymap = Keymap()
            >>> keymap.register(
            ...     Keystroke.parse(nvim, '<C-H>'),
            ...     Keystroke.parse(nvim, '<BS>'),
            ... )
            >>> keymap.register(
            ...     Keystroke.parse(nvim, '<C-H>'),
            ...     Keystroke.parse(nvim, '<BS>'),
            ...     noremap=True,
            ... )
            >>> keymap.register(
            ...     Keystroke.parse(nvim, '<C-H>'),
            ...     Keystroke.parse(nvim, '<BS>'),
            ...     nowait=True,
            ... )
            >>> keymap.register(
            ...     Keystroke.parse(nvim, '<C-H>'),
            ...     Keystroke.parse(nvim, '<BS>'),
            ...     noremap=True,
            ...     nowait=True,
            ... )

        """
        self.registry[lhs] = (lhs, rhs, noremap, nowait)

    def register_from_rule(self, nvim, rule):
        """Register a keymap from a rule.

        Args:
            nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
            rule (tuple): A rule tuple. The rule is arguments of
                ``Key.register`` method.

        Example:
            >>> from .keystroke import Keystroke
            >>> from unittest.mock import MagicMock
            >>> nvim = MagicMock()
            >>> nvim.options = {'encoding': 'utf-8'}
            >>> keymap = Keymap()
            >>> keymap.register_from_rule(nvim, [
            ...     Keystroke.parse(nvim, '<C-H>'),
            ...     Keystroke.parse(nvim, '<BS>'),
            ... ])
            >>> keymap.register_from_rule(nvim, [
            ...     Keystroke.parse(nvim, '<C-H>'),
            ...     Keystroke.parse(nvim, '<BS>'),
            ...     True,
            ... ])
            >>> keymap.register_from_rule(nvim, [
            ...     Keystroke.parse(nvim, '<C-H>'),
            ...     Keystroke.parse(nvim, '<BS>'),
            ...     True, True,
            ... ])

        """
        if len(rule) == 2:
            lhs, rhs = rule
            noremap = False
            nowait = False
        elif len(rule) == 3:
            lhs, rhs, noremap = rule
            nowait = False
        else:
            lhs, rhs, noremap, nowait = rule
        lhs = Keystroke.parse(nvim, lhs)
        rhs = Keystroke.parse(nvim, rhs)
        self.register(lhs, rhs, noremap, nowait)

    def register_from_rules(self, nvim, rules):
        """Register keymaps from rule tuple.

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
            ...     (lhs2, rhs2, True),
            ...     (lhs3, rhs3, False, True),
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
            ...     (k('<C-A><C-A>'), k('<prompt:A>')),
            ...     (k('<C-A><C-B>'), k('<prompt:B>')),
            ...     (k('<C-B><C-A>'), k('<prompt:C>')),
            ... ])
            >>> candidates = keymap.filter(k(''))
            >>> len(candidates)
            3
            >>> candidates[0]
            ((Key(...), Key(...)), (Key(code=b'<prompt:A>', ...)
            >>> candidates[1]
            ((Key(...), Key(...)), (Key(code=b'<prompt:B>', ...)
            >>> candidates[2]
            ((Key(...), Key(...)), (Key(code=b'<prompt:C>', ...)
            >>> candidates = keymap.filter(k('<C-A>'))
            >>> len(candidates)
            2
            >>> candidates[0]
            ((Key(...), Key(...)), (Key(code=b'<prompt:A>', ...)
            >>> candidates[1]
            ((Key(...), Key(...)), (Key(code=b'<prompt:B>', ...)
            >>> candidates = keymap.filter(k('<C-A><C-A>'))
            >>> len(candidates)
            1
            >>> candidates[0]
            ((Key(...), Key(...)), (Key(code=b'<prompt:A>', ...)

        Returns:
            Iterator[Keystroke]: Sorted Keystroke instances which starts from
                `lhs` Keystroke instance
        """
        candidates = (
            self.registry[k]
            for k in self.registry.keys() if k.startswith(lhs)
        )
        return sorted(candidates, key=itemgetter(0))

    def resolve(self, lhs, nowait=False):
        """Resolve ``lhs`` Keystroke instance and return resolved keystroke.

        Args:
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
            ...     (k('<C-A><C-A>'), k('<prompt:A>')),
            ...     (k('<C-A><C-B>'), k('<prompt:B>')),
            ...     (k('<C-B><C-A>'), k('<C-A><C-A>'), False),
            ...     (k('<C-B><C-B>'), k('<C-A><C-B>'), True),
            ...     (k('<C-C>'), k('<prompt:C>'), False, False),
            ...     (k('<C-C><C-A>'), k('<prompt:C1>')),
            ...     (k('<C-C><C-B>'), k('<prompt:C2>')),
            ...     (k('<C-D>'), k('<prompt:D>'), False, True),
            ...     (k('<C-D><C-A>'), k('<prompt:D1>')),
            ...     (k('<C-D><C-B>'), k('<prompt:D2>')),
            ... ])
            >>> # No mapping starts from <C-C> so <C-C> is returned
            >>> keymap.resolve(k('<C-Z>'))
            (Key(code=26, ...),)
            >>> # No single keystroke is resolved in the following case so None
            >>> # will be returned.
            >>> keymap.resolve(k('')) is None
            True
            >>> keymap.resolve(k('<C-A>')) is None
            True
            >>> # A single keystroke is resolved so rhs is returned.
            >>> # will be returned.
            >>> keymap.resolve(k('<C-A><C-A>'))
            (Key(code=b'<prompt:A>', ...),)
            >>> keymap.resolve(k('<C-A><C-B>'))
            (Key(code=b'<prompt:B>', ...),)
            >>> # noremap = False so recursively resolved
            >>> keymap.resolve(k('<C-B><C-A>'))
            (Key(code=b'<prompt:A>', ...),)
            >>> # noremap = True so resolved only once
            >>> keymap.resolve(k('<C-B><C-B>'))
            (Key(code=1, ...), Key(code=2, ...))
            >>> # nowait = False so no single keystroke could be resolved.
            >>> keymap.resolve(k('<C-C>')) is None
            True
            >>> # nowait = True so the first matched candidate is returned.
            >>> keymap.resolve(k('<C-D>'))
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
            _lhs, rhs, noremap, _nowait = candidates[0]
            if lhs == _lhs:
                return rhs if noremap else self.resolve(rhs, nowait=True)
        elif nowait:
            # Use the first matched candidate if lhs is equal
            _lhs, rhs, noremap, _nowait = candidates[0]
            if lhs == _lhs:
                return rhs if noremap else self.resolve(rhs, nowait=True)
        else:
            # Check if the current first candidate is defined as nowait
            _lhs, rhs, noremap, nowait = candidates[0]
            if nowait and lhs == _lhs:
                return rhs if noremap else self.resolve(rhs, nowait=True)
        return None

    def harvest(self, nvim, timeoutlen):
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

        Returns:
            Keystroke: A resolved keystroke.

        """
        previous = None
        while True:
            code = _getcode(
                nvim,
                datetime.now() + timeoutlen if timeoutlen else None
            )
            if code is None and previous is None:
                # timeout without input
                continue
            elif code is None:
                # timeout
                return self.resolve(previous, nowait=True) or previous
            previous = Keystroke((previous or ()) + (Key.parse(nvim, code),))
            keystroke = self.resolve(previous, nowait=False)
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
            ...     (lhs2, rhs2, True),
            ...     (lhs3, rhs3, False, True),
            ... ])

        Returns:
            Keymap: A keymap instance
        """
        keymap = cls()
        keymap.register_from_rules(nvim, rules)
        return keymap


def _getcode(nvim, timeout):
    while not timeout or timeout > datetime.now():
        code = getchar(nvim, False)
        if code != 0:
            return code
        time.sleep(0.01)
    return None


DEFAULT_KEYMAP_RULES = (
    ('<CR>', '<prompt:accept>', True),
    ('<ESC>', '<prompt:cancel>', True),
    ('<INSERT>', '<prompt:toggle_insert_mode>', True),
    ('<BS>', '<prompt:delete_char_before_caret>', True),
    ('<C-H>', '<prompt:delete_char_before_caret>', True),
    ('<DEL>', '<prompt:delete_char_under_caret>', True),
    ('<C-U>', '<prompt:delete_entire_text>', True),
    ('<Left>', '<prompt:move_caret_to_left>', True),
    ('<Right>', '<prompt:move_caret_to_right>', True),
    ('<Home>', '<prompt:move_caret_to_head>', True),
    ('<End>', '<prompt:move_caret_to_tail>', True),
    ('<C-P>', '<prompt:assign_previous_text>', True),
    ('<C-N>', '<prompt:assign_next_text>', True),
    ('<Up>', '<prompt:assign_previous_matched_text>', True),
    ('<Down>', '<prompt:assign_next_matched_text>', True),
    ('<C-R>', '<prompt:paste_from_register>', True),
    ('<C-V>', '<prompt:insert_special>', True),
    ('<C-K>', '<prompt:insert_digraph>', True),
)
