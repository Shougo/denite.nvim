"""Context module."""


class Context:
    """Context class which used to store/restore data.

    Note:
        This class defines ``__slots__`` attribute so sub-class must override
        the attribute to extend available attributes.

    Attributes:
        nvim (Nvim): The ``neovim.Nvim`` instance.
        text (str): A user input text of the prompt.
        caret_locus (int): A locus index of the caret in the prompt.

    """

    __slots__ = ('text', 'caret_locus')

    def __init__(self):
        """Constructor.

        Args:
            nvim (Nvim): The ``neovim.Nvim`` instance.

        """
        self.text = ''
        self.caret_locus = 0

    def to_dict(self):
        """Convert a context instance into a dictionary.

        Use ``Context.from_dict(d)`` to restore a context instance from a
        dictionary.

        Example:
            >>> context = Context()
            >>> context.text = 'Hello'
            >>> context.caret_locus = 3
            >>> d = context.to_dict()
            >>> d['text']
            'Hello'
            >>> d['caret_locus']
            3

        Returns:
            dict: A context dictionary.

        """
        return {
            k: getattr(self, k)
            for k in self.__slots__
        }

    def extend(self, d):
        """Extend a context instance from a dictionary.

        Use ``context.to_dict()`` to create a corresponding dictionary.
        Keys which is not in ``__slots__`` will be ignored.

        Args:
            d (dict): A dictionary.

        Example:
            >>> context = Context.from_dict({
            ...     'text': 'Hello',
            ...     'caret_locus': 3,
            ... })
            >>> context.text
            'Hello'
            >>> context.caret_locus
            3
            >>> context.extend({
            ...     'text': 'Bye',
            ...     'caret_locus': 1,
            ... })
            >>> context.text
            'Bye'
            >>> context.caret_locus
            1
        """
        for k, v in d.items():
            if k in self.__slots__:
                setattr(self, k, v)

    @classmethod
    def from_dict(cls, d):
        """Create a new context instance from a dictionary.

        Use ``context.to_dict()`` to create a corresponding dictionary.

        Args:
            d (dict): A corresponding dictionary.

        Example:
            >>> context = Context.from_dict({
            ...     'text': 'Hello',
            ...     'caret_locus': 3,
            ... })
            >>> context.text
            'Hello'
            >>> context.caret_locus
            3

        Returns:
            Context: A context instance.
        """
        context = cls.__new__(cls)
        context.extend(d)
        return context
