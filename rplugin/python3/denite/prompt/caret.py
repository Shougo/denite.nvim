"""Caret module."""


class Caret:
    """Caret (cursor) class which indicate the cursor locus in a prompt.

    Note:
        This class defines ``__slots__`` attribute so sub-class must override
        the attribute to extend available attributes.

    Attributes:
        prompt (Prompt): The ``prompt.prompt.Prompt`` instance.
    """

    __slots__ = ('prompt', '_locus')

    def __init__(self, prompt, locus=0):
        """Constructor.

        Args:
            prompt (Prompt): The ``prompt.prompt.Prompt`` instance.
            locus (int): The caret initial locus (Default: 0).
        """
        self.prompt = prompt
        self.locus = locus

    @property
    def locus(self):
        """int: Read and write current locus index of the caret in the prompt.

        When a value is smaller than the ``head`` attribute or larger than the
        ``tail`` attribute, the value is regualted to ``head`` or ``tail``.

        Example:
            >>> from unittest.mock import MagicMock
            >>> prompt = MagicMock()
            >>> prompt.text = "Hello"
            >>> caret = Caret(prompt)
            >>> caret.locus
            0
            >>> caret.locus = 3
            >>> caret.locus
            3
            >>> caret.locus = -1
            >>> caret.locus
            0
            >>> caret.locus = 100   # beyond text length
            >>> caret.locus
            5

        """
        return self._locus

    @locus.setter
    def locus(self, value):
        if value < self.head:
            self._locus = self.head
        elif value > self.tail:
            self._locus = self.tail
        else:
            self._locus = value

    @property
    def head(self):
        """int: Readonly head locus index of the caret in the prompt.

        Example:
            >>> from unittest.mock import MagicMock
            >>> prompt = MagicMock()
            >>> prompt.text = "Hello"
            >>> caret = Caret(prompt)
            >>> caret.head
            0

        """
        return 0

    @property
    def lead(self):
        """int: Readonly lead locus index of the caret in the prompt.

        The lead indicate a minimum index for a first printable character.

        Examples:
            For example, the ``lead`` become ``4`` in the following case.

            >>> from unittest.mock import MagicMock
            >>> prompt = MagicMock()
            >>> prompt.text = '    Hello world!'
            >>> caret = Caret(prompt)
            >>> caret.lead
            4
        """
        return len(self.prompt.text) - len(self.prompt.text.lstrip())

    @property
    def tail(self):
        """int: Readonly tail locus index of the caret in the prompt.

        Example:
            >>> from unittest.mock import MagicMock
            >>> prompt = MagicMock()
            >>> prompt.text = "Hello"
            >>> caret = Caret(prompt)
            >>> caret.tail
            5
        """
        return len(self.prompt.text)

    def get_backward_text(self):
        """A backward text from the caret.

        Returns:
            str: A backward part of the text from the caret

        Examples:
            >>> from unittest.mock import MagicMock
            >>> prompt = MagicMock()
            >>> # Caret:                |
            >>> prompt.text = '    Hello world!'
            >>> caret = Caret(prompt, locus=8)
            >>> caret.get_backward_text()
            '    Hell'
        """
        if self.locus == self.head:
            return ''
        return self.prompt.text[:self.locus]

    def get_selected_text(self):
        """A selected text under the caret.

        Returns:
            str: A part of the text under the caret

        Examples:
            >>> from unittest.mock import MagicMock
            >>> prompt = MagicMock()
            >>> # Caret:                |
            >>> prompt.text = '    Hello world!'
            >>> caret = Caret(prompt, locus=8)
            >>> caret.get_selected_text()
            'o'
        """
        if self.locus == self.tail or len(self.prompt.text) <= self.locus:
            return ''
        return self.prompt.text[self.locus]

    def get_forward_text(self):
        """A forward text from the caret.

        Returns:
            str: A forward part of the text from the caret

        Examples:
            >>> from unittest.mock import MagicMock
            >>> prompt = MagicMock()
            >>> # Caret:                |
            >>> prompt.text = '    Hello world!'
            >>> caret = Caret(prompt, locus=8)
            >>> caret.get_forward_text()
            ' world!'
        """
        if self.locus >= self.tail - 1:
            return ''
        return self.prompt.text[self.locus + 1:]
