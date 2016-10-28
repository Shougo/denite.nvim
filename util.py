"""Utility module."""

_cached_encoding = None


def get_encoding(nvim):
    """Return a Vim's internal encoding.

    The retrieve encoding is cached to the function instance while encoding
    options should not be changed in Vim's live session (see :h encoding) to
    enhance performance.

    Args:
        nvim (neovim.Nvim): A ``neovim.Nvim`` instance.

    Returns:
        str: A Vim's internal encoding.
    """
    global _cached_encoding
    if _cached_encoding is None:
        _cached_encoding = nvim.options['encoding']
    return _cached_encoding


def ensure_bytes(nvim, seed):
    """Encode `str` to `bytes` if necessary and return.

    Args:
        nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
        seed (AnyStr): A str or bytes instance.

    Example:
        >>> from unittest.mock import MagicMock
        >>> nvim = MagicMock()
        >>> nvim.options = {'encoding': 'utf-8'}
        >>> ensure_bytes(nvim, b'a')
        b'a'
        >>> ensure_bytes(nvim, 'a')
        b'a'

    Returns:
        bytes: A bytes represantation of ``seed``.
    """
    if isinstance(seed, str):
        encoding = get_encoding(nvim)
        return seed.encode(encoding, 'surrogateescape')
    return seed


def ensure_str(nvim, seed):
    """Decode `bytes` to `str` if necessary and return.

    Args:
        nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
        seed (AnyStr): A str or bytes instance.

    Example:
        >>> from unittest.mock import MagicMock
        >>> nvim = MagicMock()
        >>> nvim.options = {'encoding': 'utf-8'}
        >>> ensure_str(nvim, b'a')
        'a'
        >>> ensure_str(nvim, 'a')
        'a'

    Returns:
        str: A str represantation of ``seed``.
    """
    if isinstance(seed, bytes):
        encoding = get_encoding(nvim)
        return seed.decode(encoding, 'surrogateescape')
    return seed


def int2char(nvim, code):
    """Return a corresponding char of `code`.

    It uses "nr2char()" in Vim script when 'encoding' option is not utf-8.
    Otherwise it uses "chr()" in Python to improve the performance.

    Args:
        nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
        code (int): A int which represent a single character.

    Example:
        >>> from unittest.mock import MagicMock
        >>> nvim = MagicMock()
        >>> nvim.options = {'encoding': 'utf-8'}
        >>> int2char(nvim, 97)
        'a'

    Returns:
        str: A str of ``code``.
    """
    encoding = get_encoding(nvim)
    if encoding in ('utf-8', 'utf8'):
        return chr(code)
    return nvim.call('nr2char', code)


def int2repr(nvim, code):
    from .key import Key
    if isinstance(code, int):
        return int2char(nvim, code)
    return Key.represent(nvim, ensure_bytes(nvim, code))


def getchar(nvim, *args):
    """Call getchar and return int or bytes instance.

    Args:
        nvim (neovim.Nvim): A ``neovim.Nvim`` instance.
        *args: Arguments passed to getchar function in Vim.

    Returns:
        Union[int, bytes]: A int or bytes.
    """
    try:
        ret = nvim.call('getchar', *args)
        if isinstance(ret, int):
            return ret
        return ensure_bytes(nvim, ret)
    except nvim.error as e:
        # NOTE:
        # Vim returns 0x03 when ^C is pressed but Neovim.
        # Additionally, KeyboardInterrupt is not raised but
        # A general nvim.error and only the following dirty
        # implementation works.
        if str(e) == "b'Keyboard interrupt'":
            return 0x03  # ^C
        raise e


def safeget(l, index, default=None):
    """Return an index item of list or default."""
    try:
        return l[index]
    except IndexError:
        return default


# http://python-3-patterns-idioms-test.readthedocs.io/en/latest/Metaprogramming.html
class Singleton(type):
    """A singleton metaclass."""

    instance = None

    def __call__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super().__call__(*args, **kwargs)
        return cls.instance
