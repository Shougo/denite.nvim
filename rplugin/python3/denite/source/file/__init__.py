# ============================================================================
# FILE: file.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from pathlib import Path
import glob
import re

from denite.base.source import Base
from denite.util import abspath, expand, Nvim, UserContext, Candidates


class Source(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'file'
        self.kind = 'file'
        self.matchers = [
            'converter/expand_input',
            'matcher/fuzzy',
            'matcher/hide_hidden_files',
        ]
        self.is_volatile = True

    def gather_candidates(self, context: UserContext) -> Candidates:
        context['is_interactive'] = True
        candidates = []

        new = context['args'][0] if context['args'] else ''
        if new and new != 'new':
            self.error_message(context, f'invalid argument: "{new}"')

        path = (context['args'][1] if len(context['args']) > 1
                else context['path'])
        path = abspath(self.vim, path)

        inp = Path(expand(context['input']))
        filename = (str(inp) if inp.is_absolute()
                    else str(Path(path).joinpath(inp)))
        if new == 'new':
            candidates.append({
                'word': filename,
                'abbr': '[new] ' + filename,
                'action__path': abspath(self.vim, filename),
            })
        else:
            file_path = Path(filename)
            glb = str(file_path if file_path.is_dir() else file_path.parent)
            # Note: Path('../.').name convert to ".."
            hidden = re.match(r'.([^.]|$)', str(self.vim.call(
                'fnamemodify', context['input'], ':t')))
            glb += '/.*' if hidden else '/*'
            for f in glob.glob(glb):
                fullpath = abspath(self.vim, f)
                f = re.sub(r'\n', r'\\n', f)
                f_path = Path(f)
                abbr = (str(f_path.relative_to(path))
                        if fullpath != path and f.startswith(path + '/')
                        else str(f_path.resolve())) + (
                            '/' if f_path.is_dir() else '')
                candidates.append({
                    'word': f,
                    'abbr': abbr,
                    'kind': ('directory' if f_path.is_dir() else 'file'),
                    'action__path': fullpath,
                })
        return candidates
