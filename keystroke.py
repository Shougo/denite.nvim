"""Keystroke module."""
import re
from .key import Key
from .util import ensure_bytes


KEYS_PATTERN = re.compile(rb'(?:<[^>]+>|\x80\xfc.{2}|\x80.{2}|\S|\s)')


class Keystroke(tuple):
    """Keystroke class which indicate multiple keys."""

    __hash__ = tuple.__hash__
    __slots__ = ()

    def __str__(self):
        """Return a string representation of the keystroke."""
        return ''.join(str(k) for k in self)

    def startswith(self, other):
        """Check if the keystroke starts from ``other``.

        Args:
            other (Keystroke): A keystroke instance will be checked.

        Returns:
            bool: True if the keystroke starts from ``other``.
        """
        if len(self) < len(other):
            return False
        return all(lhs == rhs for lhs, rhs in zip(self, other))

    @classmethod
    def parse(cls, nvim, expr):
        r"""Parse a keystroke expression and return a Keystroke instance.

        Args:
            nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
            expr (tuple, bytes, str): A keystroke expression.

        Example:
            >>> from unittest.mock import MagicMock
            >>> nvim = MagicMock()
            >>> nvim.options = {'encoding': 'utf-8'}
            >>> Keystroke.parse(nvim, 'abc')
            (Key(code=97, ...), Key(code=98, ...), Key(code=99, ...))
            >>> Keystroke.parse(nvim, '<Insert>')
            (Key(code=b'\x80kI', char=''),)

        Returns:
            Keystroke: A Keystroke instance.
        """
        keys = _ensure_keys(nvim, expr)
        instance = cls(keys)
        return instance


def _ensure_keys(nvim, expr):
    if isinstance(expr, (bytes, str)):
        expr_bytes = ensure_bytes(nvim, expr)
        keys = tuple(
            Key.parse(nvim, k)
            for k in KEYS_PATTERN.findall(expr_bytes)
        )
    else:
        keys = tuple(expr)
    return keys
