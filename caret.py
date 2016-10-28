"""Caret module."""


class Caret:
    """Caret (cursor) class which indicate the cursor locus in a prompt.

    Note:
        This class defines ``__slots__`` attribute so sub-class must override
        the attribute to extend available attributes.

    Attributes:
        context (Context): The ``prompt.context.Context`` instance.
    """

    __slots__ = ('context',)

    def __init__(self, context):
        """Constructor.

        Args:
            context (Context): The ``prompt.context.Context`` instance.
        """
        self.context = context

    @property
    def locus(self):
        """int: Read and write current locus index of the caret in the prompt.

        When a value is smaller than the ``head`` attribute or larger than the
        ``tail`` attribute, the value is regualted to ``head`` or ``tail``.

        Example:
            >>> from .context import Context
            >>> context = Context()
            >>> context.text = "Hello"
            >>> caret = Caret(context)
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
        return self.context.caret_locus

    @locus.setter
    def locus(self, value):
        if value < self.head:
            self.context.caret_locus = self.head
        elif value > self.tail:
            self.context.caret_locus = self.tail
        else:
            self.context.caret_locus = value

    @property
    def head(self):
        """int: Readonly head locus index of the caret in the prompt.

        Example:
            >>> from .context import Context
            >>> context = Context()
            >>> context.text = "Hello"
            >>> caret = Caret(context)
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

            >>> from .context import Context
            >>> context = Context()
            >>> context.text = '    Hello world!'
            >>> caret = Caret(context)
            >>> caret.lead
            4
        """
        return len(self.context.text) - len(self.context.text.lstrip())

    @property
    def tail(self):
        """int: Readonly tail locus index of the caret in the prompt.

        Example:
            >>> from .context import Context
            >>> context = Context()
            >>> context.text = "Hello"
            >>> caret = Caret(context)
            >>> caret.tail
            5
        """
        return len(self.context.text)

    def get_backward_text(self):
        """A backward text from the caret.

        Returns:
            str: A backward part of the text from the caret

        Examples:
            >>> from .context import Context
            >>> context = Context()
            >>> # Caret:                |
            >>> context.text = '    Hello world!'
            >>> context.caret_locus = 8
            >>> caret = Caret(context)
            >>> caret.get_backward_text()
            '    Hell'
        """
        if self.locus == self.head:
            return ''
        return self.context.text[:self.locus]

    def get_selected_text(self):
        """A selected text under the caret.

        Returns:
            str: A part of the text under the caret

        Examples:
            >>> from .context import Context
            >>> context = Context()
            >>> # Caret:                |
            >>> context.text = '    Hello world!'
            >>> context.caret_locus = 8
            >>> caret = Caret(context)
            >>> caret.get_selected_text()
            'o'
        """
        if self.locus == self.tail:
            return ''
        return self.context.text[self.locus]

    def get_forward_text(self):
        """A forward text from the caret.

        Returns:
            str: A forward part of the text from the caret

        Examples:
            >>> from .context import Context
            >>> context = Context()
            >>> # Caret:                |
            >>> context.text = '    Hello world!'
            >>> context.caret_locus = 8
            >>> caret = Caret(context)
            >>> caret.get_forward_text()
            ' world!'
        """
        if self.locus >= self.tail - 1:
            return ''
        return self.context.text[self.locus + 1:]
