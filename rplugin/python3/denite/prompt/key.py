"""Key module."""
from collections import namedtuple
from .util import ensure_bytes, ensure_str, int2char
from typing import Dict  # noqa: F401


ESCAPE_QUOTE = str.maketrans({
    '"': '\\"',
})

CTRL_KEY = b'\x80\xfc\x04'
META_KEY = b'\x80\xfc\x08'
CTRL_SHIFT_KEY = b'\x80\xfc\x06'

# :help key-notation
SPECIAL_KEYS = {
    'C-@': b'\x80\xffX',    # Vim internally use <80><ff>X for <C-@>
    'NUL': 10,
    'BS': b'\x80kb',
    'TAB': 9,
    'S-TAB': b'\x80kB',
    'NL': 10,
    'FE': 12,
    'CR': 13,
    'ESC': 27,
    'SPACE': 32,
    'LT': 60,
    'BSLASH': 92,
    'BAR': 124,
    'DEL': b'\x80kD',
    'CSI': b'\x9B',
    'XCSI': b'\x80\xfdP',
    'UP': b'\x80ku',
    'DOWN': b'\x80kd',
    'LEFT': b'\x80kl',
    'RIGHT': b'\x80kr',
    'S-UP': b'\x80\xfd',
    'S-DOWN': b'\x80\xfd',
    'S-LEFT': b'\x80#4',
    'S-RIGHT': b'\x80%i',
    'C-LEFT': b'\x80\xfdT',
    'C-RIGHT': b'\x80\xfdU',
    'F1': b'\x80k1',
    'F2': b'\x80k2',
    'F3': b'\x80k3',
    'F4': b'\x80k4',
    'F5': b'\x80k5',
    'F6': b'\x80k6',
    'F7': b'\x80k7',
    'F8': b'\x80k8',
    'F9': b'\x80k9',
    'F10': b'\x80k;',
    'F11': b'\x80F1',
    'F12': b'\x80F2',
    'S-F1': b'\x80\xfd\x06',
    'S-F2': b'\x80\xfd\x07',
    'S-F3': b'\x80\xfd\x08',
    'S-F4': b'\x80\xfd\x09',
    'S-F5': b'\x80\xfd\x0A',
    'S-F6': b'\x80\xfd\x0B',
    'S-F7': b'\x80\xfd\x0C',
    'S-F8': b'\x80\xfd\x0D',
    'S-F9': b'\x80\xfd\x0E',
    'S-F10': b'\x80\xfd\x0F',
    'S-F11': b'\x80\xfd\x10',
    'S-F12': b'\x80\xfd\x11',
    'HELP': b'\x80%1',
    'UNDO': b'\x80&8',
    'INSERT': b'\x80kI',
    'HOME': b'\x80kh',
    'END': b'\x80@7',
    'PAGEUP': b'\x80kP',
    'PAGEDOWN': b'\x80kN',
    'KHOME': b'\x80K1',
    'KEND': b'\x80K4',
    'KPAGEUP': b'\x80K3',
    'KPAGEDOWN': b'\x80K5',
    'KPLUS': b'\x80K6',
    'KMINUS': b'\x80K7',
    'KMULTIPLY': b'\x80K9',
    'KDIVIDE': b'\x80K8',
    'KENTER': b'\x80KA',
    'KPOINT': b'\x80KB',
    'K0': b'\x80KC',
    'K1': b'\x80KD',
    'K2': b'\x80KE',
    'K3': b'\x80KF',
    'K4': b'\x80KG',
    'K5': b'\x80KH',
    'K6': b'\x80KI',
    'K7': b'\x80KJ',
    'K8': b'\x80KK',
    'K9': b'\x80KL',
    'SCROLLWHEELUP': b'\x80\xfdK',
    'SCROLLWHEELDOWN': b'\x80\xfdL',
    'TSCROLLWHEELUP': b'\x80ku',
    'TSCROLLWHEELDOWN': b'\x80kd',
}
SPECIAL_KEYS_REVRESE = {v: k for k, v in SPECIAL_KEYS.items()}

# Add aliases used in Vim. This requires to be AFTER making swap dictionary
SPECIAL_KEYS.update({
    'NOP': SPECIAL_KEYS['NUL'],
    'RETURN': SPECIAL_KEYS['CR'],
    'ENTER': SPECIAL_KEYS['CR'],
    'BACKSPACE': SPECIAL_KEYS['BS'],
    'DELETE': SPECIAL_KEYS['DEL'],
    'INS': SPECIAL_KEYS['INSERT'],
})


KeyBase = namedtuple('KeyBase', ['code', 'char'])


class Key(KeyBase):
    """Key class which indicate a single key.

    Attributes:
        code (int or bytes): A code of the key. A bytes is used when the key is
            a special key in Vim (a key which starts from 0x80 in getchar()).
        char (str): A printable represantation of the key. It might be an empty
            string when the key is not printable.
    """

    __slots__ = ()
    __cached = {}  # type: Dict[str, Key]

    def __str__(self):
        """Return string representation of the key."""
        return self.char

    @classmethod
    def represent(cls, nvim, code):
        """Return a string representation of a Keycode."""
        if isinstance(code, int):
            return int2char(nvim, code)
        if code in SPECIAL_KEYS_REVRESE:
            char = SPECIAL_KEYS_REVRESE.get(code)
            return '<%s>' % char
        else:
            return ensure_str(nvim, code)

    @classmethod
    def parse(cls, nvim, expr):
        r"""Parse a key expression and return a Key instance.

        It returns a Key instance of a key expression. The instance is cached
        to individual expression so that the instance is exactly equal when
        same expression is spcified.

        Args:
            expr (int, bytes, or str): A key expression.

        Example:
            >>> from unittest.mock import MagicMock
            >>> nvim = MagicMock()
            >>> nvim.options = {'encoding': 'utf-8'}
            >>> Key.parse(nvim, ord('a'))
            Key(code=97, char='a')
            >>> Key.parse(nvim, '<Insert>')
            Key(code=b'\x80kI', char='')

        Returns:
            Key: A Key instance.
        """
        if expr not in cls.__cached:
            code = _resolve(nvim, expr)
            if isinstance(code, int):
                char = int2char(nvim, code)
            elif not code.startswith(b'\x80'):
                char = ensure_str(nvim, code)
            else:
                char = ''
            cls.__cached[expr] = cls(code, char)
        return cls.__cached[expr]


def _resolve(nvim, expr):
    if isinstance(expr, int):
        return expr
    elif isinstance(expr, str):
        return _resolve(nvim, ensure_bytes(nvim, expr))
    elif isinstance(expr, bytes):
        if len(expr) == 1:
            return ord(expr)
        elif expr.startswith(b'\x80'):
            return expr
    else:
        raise AttributeError((
            '`expr` (%s) requires to be an instance of int|bytes|str but '
            '"%s" has specified.'
        ) % (expr, type(expr)))
    # Special key
    if expr.startswith(b'<') or expr.endswith(b'>'):
        inner = expr[1:-1]
        code = _resolve_from_special_keys(nvim, inner)
        if code != inner:
            return code
    return expr


def _resolve_from_special_keys(nvim, inner):
    inner_upper = inner.upper()
    inner_upper_str = ensure_str(nvim, inner_upper)
    if inner_upper_str in SPECIAL_KEYS:
        return SPECIAL_KEYS[inner_upper_str]
    elif inner_upper.startswith(b'C-S-') or inner_upper.startswith(b'S-C-'):
        return b''.join([
            CTRL_SHIFT_KEY,
            _resolve_from_special_keys_inner(nvim, inner[4:]),
        ])
    elif inner_upper.startswith(b'C-'):
        if len(inner) == 3:
            if inner_upper[-1] in b'@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_?':
                return inner[-1] & 0x1f
        return b''.join([
            CTRL_KEY,
            _resolve_from_special_keys_inner(nvim, inner[2:]),
        ])
    elif inner_upper.startswith(b'M-') or inner_upper.startswith(b'A-'):
        return b''.join([
            META_KEY,
            _resolve_from_special_keys_inner(nvim, inner[2:]),
        ])
    elif inner_upper == b'LEADER':
        leader = nvim.vars.get('mapleader', '\\')
        leader = ensure_bytes(nvim, leader)
        return _resolve(nvim, leader)
    elif inner_upper == b'LOCALLEADER':
        leader = nvim.vars.get('maplocalleader', '\\')
        leader = ensure_bytes(nvim, leader)
        return _resolve(nvim, leader)
    return inner


def _resolve_from_special_keys_inner(nvim, inner):
    code = _resolve_from_special_keys(nvim, inner)
    if isinstance(code, int):
        return ensure_bytes(nvim, int2char(nvim, code))
    return ensure_bytes(nvim, code)
