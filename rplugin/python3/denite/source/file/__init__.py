# ============================================================================
# FILE: file.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from os import sep
from pathlib import Path
from pynvim import Nvim
import glob
import re

from denite.base.source import Base
from denite.util import abspath, expand, UserContext, Candidates


class Source(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'file'
        self.kind = 'file'
        self.matchers = [
            'converter/expand_input',
            'matcher/fuzzy',
        ]
        self.is_volatile = True

    def gather_candidates(self, context: UserContext) -> Candidates:
        context['is_interactive'] = True
        candidates = []

        arg = context['args'][0] if context['args'] else ''
        if arg and arg != 'new' and arg != 'hidden':
            self.error_message(context, f'invalid argument: "{arg}"')

        path = (context['args'][1] if len(context['args']) > 1
                else context['path'])
        path = abspath(self.vim, path)

        inp = Path(expand(context['input']))
        filename = (str(inp) if inp.is_absolute()
                    else str(Path(path).joinpath(inp)))
        if arg == 'new':
            candidates.append({
                'word': filename,
                'abbr': '[new] ' + filename,
                'action__path': abspath(self.vim, filename),
            })
        else:
            file_path = Path(filename)
            glb = str(file_path if file_path.is_dir() else file_path.parent)
            # Note: Path('../.').name convert to ".."
            hidden = arg == 'hidden' or re.match(
                r'\.([^.]|$)', str(self.vim.call(
                    'fnamemodify', context['input'], ':t')))
            glb += '/.*' if hidden else '/*'
            glb = re.sub(r'//', r'/', glb)
            for f in glob.glob(glb):
                f = re.sub(r'\n', r'\\n', f)

                fullpath = abspath(self.vim, f)
                f_path = Path(f)
                abbr = (str(f_path.relative_to(path))
                        if fullpath != path and f.startswith(path + sep)
                        else fullpath) + (sep if f_path.is_dir() else '')
                candidates.append({
                    'word': f,
                    'abbr': abbr,
                    'kind': ('directory' if f_path.is_dir() else 'file'),
                    'action__path': fullpath,
                })
        return candidates
