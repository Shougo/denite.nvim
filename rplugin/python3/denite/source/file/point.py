# ============================================================================
# FILE: file/point.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from pathlib import Path
from pynvim import Nvim
from re import sub, match

from denite.base.source import Base
from denite.util import parse_jump_line, abspath
from denite.util import UserContext, Candidates


class Source(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'file/point'
        self.kind = 'file'

    def on_init(self, context: UserContext) -> None:
        context['__line'] = self.vim.call('getline', '.')
        context['__cfile'] = self.vim.call('expand', '<cfile>')

    def gather_candidates(self, context: UserContext) -> Candidates:
        result = parse_jump_line(
            self.vim.call('getcwd'), context['__line'])
        if result and Path(result[0]).is_file():
            return [{
                'word': '{}: {}{}: {}'.format(
                    result[0], result[1],
                    (':' + result[2] if result[2] != '0' else ''),
                    result[3]),
                'action__path': result[0],
                'action__line': result[1],
                'action__col': result[2],
            }]

        cfile = context['__cfile']
        cpath = Path(abspath(self.vim, cfile))
        if match('[./]+$', cfile):
            return []
        if cpath.exists() and cpath.is_file():
            return [{'word': cfile,
                     'action__path': abspath(self.vim, cfile)}]
        if _checkhost(cfile) or match(
                r'https?://(127\.0\.0\.1|localhost)[:/]', cfile):
            return [{'word': cfile, 'action__path': cfile}]
        return []


def _checkhost(path: str) -> str:
    if not match(r'https?://', path):
        return ''
    try:
        # "import socket" may not work in Windows?
        from socket import gethostbyname
        return gethostbyname(sub(r'/.*$', '', sub(r'^\w+://', '', path)))
    except Exception:
        return ''
