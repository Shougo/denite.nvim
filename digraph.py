"""Digraph module."""
import re
from .key import Key
from .util import Singleton, getchar, int2char


DIGRAPH_PATTERN = re.compile(r'(\S{2})\s+(\S)+\s+\d+')
"""A digraph pattern used to find digraphs in digraph buffer."""


class Digraph(metaclass=Singleton):
    """A digraph registry singleton class.

    Note:
        This class defines ``__slots__`` attribute so sub-class must override
        the attribute to extend available attributes.

    Attributes:
        registry (dict): A cached digraph registry.
    """

    __slots__ = ('registry',)

    def __init__(self):
        """Constructor."""
        self.registry = None

    def find(self, nvim, char1, char2):
        """Find a digraph of char1/char2.

        Args:
            nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
            char1 (str): A char1 for a digraph.
            char2 (str): A char2 for a digraph.

        Return:
            str: A digraph character.
        """
        if self.registry is None:
            digraph_output = nvim.call('execute', 'digraphs')
            self.registry = _parse_digraph_output(digraph_output)
        if char1 + char2 not in self.registry:
            return self.registry.get(char2 + char1, char2)
        return self.registry[char1 + char2]

    def retrieve(self, nvim):
        """Retrieve char1/char2 and return a corresponding digraph.

        It asks users to hit two characters which indicate a digraph.

        Args:
            nvim (neovim.Nvim): A ``neovim.Nvim`` instance.

        Return:
            str: A digraph character.
        """
        code1 = getchar(nvim)
        if isinstance(code1, bytes) and code1.startswith(b'\x80'):
            return Key.represent(nvim, code1)
        code2 = getchar(nvim)
        if isinstance(code2, bytes) and code2.startswith(b'\x80'):
            return Key.represent(nvim, code2)
        char1 = int2char(nvim, code1)
        char2 = int2char(nvim, code2)
        return self.find(nvim, char1, char2)


def _parse_digraph_output(output):
    output = output.replace('\n', '')
    output = output.replace('\r', '')
    return {
        m.group(1): m.group(2)
        for m in DIGRAPH_PATTERN.finditer(output)
    }
