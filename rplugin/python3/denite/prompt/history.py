"""Command-line history module."""


class History:
    """History class which manage a Vim's command-line history for input.

    Note:
        This class defines ``__slots__`` attribute so sub-class must override
        the attribute to extend available attributes.

    Attributes:
        prompt (Prompt): The ``prompt.prompt.Prompt`` instance.
    """

    __slots__ = ('prompt', '_index', '_cached', '_backward', '_threshold')

    def __init__(self, prompt):
        """Constructor.

        Args:
            prompt (Prompt): The ``prompt.prompt.Prompt`` instance.
        """
        self.prompt = prompt
        self._index = 0
        self._cached = prompt.text
        self._backward = prompt.caret.get_backward_text()
        self._threshold = 0

    @property
    def nvim(self):
        """A ``neovim.Nvim`` instance."""
        return self.prompt.nvim

    def current(self):
        """Current command-line history value of input.

        Returns:
            str: A current command-line history value of input which an
                internal index points to. It returns a cached value when the
                internal index points to 0.
        """
        if self._index == 0:
            return self._cached
        return self.nvim.call('histget', 'input', -self._index)

    def previous(self):
        """Get previous command-line history value of input.

        It increases an internal index and points to a previous command-line
        history value.

        Note that it cahces a ``prompt.text`` when the internal index was 0 (an
        initial value) and the cached value is used when the internal index
        points to 0.
        This behaviour is to mimic a Vim's builtin command-line history
        behaviour.

        Returns:
            str: A previous command-line history value of input.
        """
        if self._index == 0:
            self._cached = self.prompt.text
            self._threshold = self.nvim.call('histnr', 'input')
        if self._index < self._threshold:
            self._index += 1
        return self.current()

    def next(self):
        """Get next command-line history value of input.

        It decreases an internal index and points to a next command-line
        history value.

        Returns:
            str: A next command-line history value of input.
        """
        if self._index == 0:
            self._cached = self.prompt.text
            self._threshold = self.nvim.call('histnr', 'input')
        if self._index > 0:
            self._index -= 1
        return self.current()

    def previous_match(self):
        """
        Get previous matched command-line history value of input.

        The initial query text is a text before the cursor when an internal
        index was 0 (like a cached value but only before the cursor.)
        It increases an internal index until a previous command-line history
        value matches to an initial query text and points to the matched
        previous history value.
        This behaviour is to mimic a Vim's builtin command-line history
        behaviour.

        Returns:
            str: A matched previous command-line history value of input.
        """
        if self._index == 0:
            self._backward = self.prompt.caret.get_backward_text()
        index = _index = self._index - 1
        while _index < self._index:
            _index = self._index
            candidate = self.previous()
            if candidate.startswith(self._backward):
                return candidate
        self._index = index
        return self.previous()

    def next_match(self):
        """Get next matched command-line history value of input.

        The initial query text is a text before the cursor when an internal
        index was 0 (like a cached value but only before the cursor.)
        It decreases an internal index until a next command-line history value
        matches to an initial query text and points to the matched next
        command-line history value.
        This behaviour is to mimic a Vim's builtin command-line history
        behaviour.

        Returns:
            str: A matched next command-line history value of input.
        """
        if self._index == 0:
            return self._cached
        index = _index = self._index + 1
        while _index > self._index:
            _index = self._index
            candidate = self.next()
            if candidate.startswith(self._backward):
                return candidate
        self._index = index
        return self.next()
