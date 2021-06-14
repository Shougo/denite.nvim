# ============================================================================
# FILE: util.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

from glob import glob
from os import access, sep, walk, R_OK
from os.path import expandvars
from pathlib import Path
from pynvim import Nvim
from sys import executable, base_exec_prefix
import importlib.util
import inspect
import re
import shutil
import sys
import traceback
import typing

UserContext = typing.Dict[str, typing.Any]
Candidate = typing.Dict[str, typing.Any]
Candidates = typing.List[Candidate]


def set_default(vim: Nvim, var: str, val: typing.Any) -> typing.Any:
    return vim.call('denite#util#set_default', var, val)


def convert2list(expr: typing.Any) -> typing.List[typing.Any]:
    return (expr if isinstance(expr, list) else [expr])


def globruntime(runtimepath: str, path: str) -> typing.List[str]:
    ret: typing.List[str] = []
    for rtp in re.split(',', runtimepath):
        ret += glob(rtp + '/' + path)
    return ret


def echo(vim: Nvim, color: str, string: str) -> None:
    vim.call('denite#util#echo', color, string)


def debug(vim: Nvim, expr: typing.Any) -> None:
    if hasattr(vim, 'out_write'):
        string = (expr if isinstance(expr, str) else str(expr))
        vim.out_write('[denite] ' + string + '\n')
    else:
        print(expr)


def error(vim: Nvim, expr: typing.Any) -> None:
    string = (expr if isinstance(expr, str) else str(expr))
    vim.call('denite#util#print_error', string)


def error_tb(vim: Nvim, msg: str) -> None:
    lines: typing.List[str] = []
    t, v, tb = sys.exc_info()
    if t and v and tb:
        lines += traceback.format_exc().splitlines()
    lines += ['%s.  Use :messages / see above for error details.' % msg]
    if hasattr(vim, 'err_write'):
        vim.err_write('[denite] %s\n' % '\n'.join(lines))
    else:
        for line in lines:
            error(vim, line)


def clear_cmdline(vim: Nvim) -> None:
    vim.command('redraw | echo')


def escape(expr: str) -> str:
    return expr.replace("'", "''")


def regex_convert_str_vim(string: str) -> str:
    return re.sub(r'([\^$.*\\/~\[\]])', r'\\\1', string)


def regex_convert_py_vim(expr: str) -> str:
    return r'\v' + re.sub(r'(?!\\)([/~])', r'\\\1', expr)


def escape_fuzzy(string: str) -> str:
    # Escape string for python regexp.
    p = re.sub(r'([a-zA-Z0-9_-])(?!$)', r'\1[^\1]*', string)
    p = re.sub(r'/(?!$)', r'/[^/]*', p)
    return p


def get_custom(custom: typing.Dict[str, typing.Any], kind: str,
               name: str, key: str, default: typing.Any) -> typing.Any:
    custom_val = custom[kind]
    if name not in custom_val:
        return get_custom(custom, kind, '_', key, default)
    elif key in custom_val[name]:
        return custom_val[name][key]
    elif key in custom_val['_']:
        return custom_val['_'][key]
    else:
        return default


def load_external_module(base: str, module: str) -> None:
    current = Path(base).resolve().parent
    module_dir = current.parent.joinpath(module)
    sys.path.insert(0, str(module_dir))


def readable(path: Path) -> bool:
    try:
        if access(str(path), R_OK) and path.resolve():
            return True
        else:
            return False
    except Exception:
        return False


def split_input(text: str) -> typing.List[str]:
    return [re.sub(r'\\(?=\s)', '', x) for x in
            re.split(r'(?<!\\)\s+', text) if x != ''] if text else ['']


def path2dir(path: str) -> str:
    return path if Path(path).is_dir() else str(Path(path).parent)


def path2project(vim: Nvim, path: str,
                 root_markers: typing.List[str]) -> str:
    return str(vim.call('denite#project#path2project_directory',
                        path, root_markers))


def parse_jump_line(path_head: str, line: str) -> typing.List[str]:
    m = re.search(r'^(.*?):(\d+)(?::(\d+))?:(.*)$', line)
    if not m or not m.group(1) or not m.group(4):
        return []

    if re.search(r':\d+$', m.group(1)):
        # Use column pattern
        m = re.search(r'^(.*?):(\d+):(\d+):(.*)$', line)

    [path, linenr, col, text] = m.groups()  # type: ignore

    if not linenr:
        linenr = '1'
    if not col:
        col = '0'
    if not Path(path).is_absolute():
        path = str(Path(path_head).joinpath(path))

    return [path, linenr, col, text]


def expand(path: str) -> str:
    if path.startswith('~'):
        try:
            path = str(Path(path).expanduser())
        except Exception:
            pass
    return expandvars(path)


def abspath(vim: Nvim, pathstr: str) -> str:
    path = Path(expand(pathstr))
    if not path.is_absolute():
        path = Path(vim.call('getcwd')).joinpath(pathstr)
    if readable(path):
        path = path.resolve()
    return str(path)


def relpath(vim: Nvim, path: str) -> str:
    return str(Path(vim.call('fnamemodify', expand(path), ':~:.')))


def convert2fuzzy_pattern(text: str) -> str:
    def esc(string: str) -> str:
        # Escape string for convert2fuzzy_pattern.
        p = re.sub(r'([a-zA-Z0-9_-])(?!$)', r'\1[^\1 \t]{-}', string)
        p = re.sub(r'/(?!$)', r'/[^/]*', p)
        return p
    return '|'.join([esc(x) for x in split_input(text)])


def convert2regex_pattern(text: str) -> str:
    return '|'.join(split_input(text))


def parse_command(array: typing.List[str],
                  **kwargs: typing.Any) -> typing.List[str]:
    def parse_arg(arg: str) -> str:
        if arg.startswith(':') and arg[1:] in kwargs:
            return str(kwargs[arg[1:]])
        return arg

    return [parse_arg(i) for i in array]


def find_rplugins(context: UserContext, source: str,
                  loaded_paths: typing.List[str]) -> typing.Generator[
                      typing.Tuple[str, str], None, None]:
    """Find available modules from runtimepath and yield

    It searches modules from rplugin/python3/denite/{source} recursively
    and yields path and module path (dot separated path)

    Search will be performed with the following rules

    1.  Ignore {source,kind,filter}/__init__.py while it has no
        implementation
    2.  Ignore {source,filter}/base.py while it only has an abstract
        implementation. Note that kind/base.py DOES have an
        implementation so it should NOT be ignored
    3   {source,kind,filter}/{foo.py,foo/__init__.py} is handled as
        a module foo
    4.  {source,kind,filter}/foo/{bar.py,bar/__init__.py} is handled
        as a module foo.bar

    Args:
        context (dict): A context dictionary
        source (str): 'source', 'kind', or 'filter'
        loaded_paths: (str[]): Loaded module path list

    Yields:
        (path, module_path)

        path (str): A path of the module
        module_path (str): A dot separated module path used to import
    """
    base = str(Path('rplugin').joinpath('python3', 'denite', source))
    for runtime in context.get('runtimepath', '').split(','):
        root = Path(runtime).joinpath(base)
        for r, _, fs in walk(str(root)):
            for f in fs:
                path = str(Path(r).joinpath(f))
                if not path.endswith('.py') or path in loaded_paths:
                    continue
                # Remove ext
                module_path = str(Path(path).relative_to(root))[: -3]
                if module_path == '__init__':
                    # __init__.py in {root} does not have implementation
                    # so skip
                    continue
                if Path(module_path).name == '__init__':
                    # 'foo/__init__.py' should be loaded as a module 'foo'
                    module_path = str(Path(module_path).parent)
                # Convert IO path to module path
                module_str = module_path.replace(sep, '.')
                yield (path, module_str)


def import_rplugins(name: str, context: UserContext, source: str,
                    loaded_paths: typing.List[str]) -> typing.Generator[
                        typing.Tuple[typing.Any, str, str], None, None]:
    """Import available module and yield specified attr

    It uses 'find_rplugins' to find available modules and yield
    a specified attribute.

    It raises AttributeError when the module does not have a
    specified attribute except the module file name is '__init__.py'
    which may exist only for making a module namespace.
    """
    for path, module_path in find_rplugins(context, source, loaded_paths):
        module_name = 'denite.%s.%s' % (source, module_path)
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore
        if (not hasattr(module, name) or
                inspect.isabstract(getattr(module, name))):
            continue
        yield (getattr(module, name), path, module_path)


def parse_tagline(line: str, tagpath: str) -> typing.Dict[str, typing.Any]:
    elem = line.split("\t")
    file_path = Path(elem[1])
    if not file_path.exists():
        file_path = Path(tagpath).parent.joinpath(elem[1])
    if readable(file_path):
        file_path = file_path.resolve()
    info = {
        'name': elem[0],
        'file': str(file_path),
        'pattern': '',
        'line': '',
        'type': '',
        'ref': '',
    }

    rest = '\t'.join(elem[2:])
    m = re.search(r'.*;"', rest)
    if not m:
        # Old format
        if len(elem) >= 3:
            if re.match(r'\d+$', elem[2]):
                info['line'] = elem[2]
            else:
                info['pattern'] = re.sub(
                    r'([~.*\[\]])', r'\\\1',
                    re.sub(r'^/|/;"$', '', elem[2]))
        return info

    pattern = m.group(0)
    if re.match(r'\d+;"$', pattern):
        info['line'] = re.sub(r';"$', '', pattern)
    else:
        info['pattern'] = re.sub(r'([~.*\[\]])', r'\\\1',
                                 re.sub(r'^/|/;"$', '', pattern))

    elem = rest[len(pattern)+1:].split("\t")
    if len(elem) >= 1:
        info['type'] = elem[0]
    info['ref'] = ' '.join(elem[1:])

    return info


def clearmatch(vim: Nvim) -> None:
    if not vim.call('exists', 'w:denite_match_id'):
        return

    # For async RPC error
    vim.command('silent! call matchdelete({})'.format(
        vim.current.window.vars['denite_match_id']))
    vim.command('silent! unlet w:denite_match_id')


def strwidth(vim: Nvim, word: str) -> int:
    return (int(vim.call('strwidth', word))
            if len(word) != len(bytes(word, 'utf-8',
                                      'surrogatepass')) else len(word))


def truncate(vim: Nvim, word: str, max_length: int) -> str:
    if (strwidth(vim, word) > max_length or
            len(word) != len(bytes(word, 'utf-8', 'surrogatepass'))):
        return str(vim.call(
            'denite#util#truncate',
            word, max_length, int(max_length / 2), '...'))

    return word


def get_python_exe() -> str:
    if 'py' in str(Path(executable).name):
        return executable

    for exe in ['python3', 'python']:
        which = shutil.which(exe)
        if which is not None:
            return which

    for name in (Path(base_exec_prefix).joinpath(v) for v in [
            'python3', 'python',
            str(Path('bin').joinpath('python3')),
            str(Path('bin').joinpath('python')),
    ]):
        if name.exists():
            return str(name)

    # return sys.executable anyway. This may not work on windows
    return executable


def safe_call(fn: typing.Callable[..., typing.Any],
              fallback: typing.Optional[bool] = None) -> typing.Any:
    """
    Ignore Exception when calling {fn}
    """
    try:
        return fn()
    except Exception:
        return fallback
