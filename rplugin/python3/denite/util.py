# ============================================================================
# FILE: util.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import importlib.util
import inspect
import re
import os
import sys
import traceback
import typing

from glob import glob
from os.path import normpath, normcase, join, dirname, exists

if importlib.util.find_spec('pynvim'):
    from pynvim import Nvim
    from pynvim.api import Buffer
else:
    from neovim import Nvim
    from neovim.api import Buffer  # noqa

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
    current = os.path.dirname(os.path.abspath(base))
    module_dir = join(os.path.dirname(current), module)
    sys.path.insert(0, module_dir)


def split_input(text: str) -> typing.List[str]:
    return [x for x in re.split(r'\s+', text) if x != ''] if text else ['']


def path2dir(path: str) -> str:
    return path if os.path.isdir(path) else os.path.dirname(path)


def path2project(vim: Nvim, path: str,
                 root_markers: typing.List[str]) -> str:
    return str(vim.call('denite#project#path2project_directory',
                        path, root_markers))


def parse_jump_line(path_head: str, line: str) -> typing.List[str]:
    m = re.search(r'^((?:[a-zA-Z]:)?[^:]*):(\d+)(?::(\d+))?:(.*)$', line)
    if not m or not m.group(1) or not m.group(4):
        return []

    if re.search(r':\d+$', m.group(1)):
        # Use column pattern
        m = re.search(r'^((?:[a-zA-Z]:)?[^:]*):(\d+):(\d+):(.*)$', line)

    [path, linenr, col, text] = m.groups()  # type: ignore

    if not linenr:
        linenr = '1'
    if not col:
        col = '0'
    if not os.path.isabs(path):
        path = join(path_head, path)

    return [path, linenr, col, text]


def expand(path: str) -> str:
    return os.path.expandvars(os.path.expanduser(path))


def abspath(vim: Nvim, path: str) -> str:
    return normpath(join(vim.call('getcwd'), expand(path)))


def relpath(vim: Nvim, path: str) -> str:
    return str(normpath(vim.call('fnamemodify', expand(path), ':~:.')))


def convert2fuzzy_pattern(text: str) -> str:
    def esc(string: str) -> str:
        # Escape string for convert2fuzzy_pattern.
        p = re.sub(r'([a-zA-Z0-9_-])(?!$)', r'\1[^\1]{-}', string)
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


# XXX: It override the builtin 'input()' function.
def input(vim: Nvim, context: UserContext,
          prompt: str = '', text: str = '', completion: str = '') -> str:
    try:
        if completion != '':
            return str(vim.call('input', prompt, text, completion))
        else:
            return str(vim.call('input', prompt, text))
    except vim.error as e:
        # NOTE:
        # neovim raise nvim.error instead of KeyboardInterrupt when Ctrl-C
        # has pressed so treat it as a real KeyboardInterrupt exception.
        if str(e) != "b'Keyboard interrupt'":
            raise e
    except KeyboardInterrupt:
        pass
    # Ignore the interrupt
    return ''


def find_rplugins(context: UserContext, source: str,
                  loaded_paths: typing.List[str]) -> typing.Generator[
                      typing.Tuple[str, str], None, None]:
    """Find available modules from runtimepath and yield

    It searches modules from rplugin/python3/denite/{source} recursvely
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
    base = join('rplugin', 'python3', 'denite', source)
    for runtime in context.get('runtimepath', '').split(','):
        root = normcase(normpath(join(runtime, base)))
        for r, _, fs in os.walk(root):
            for f in fs:
                path = normcase(normpath(join(r, f)))
                if not path.endswith('.py') or path in loaded_paths:
                    continue
                module_path = os.path.relpath(path, root)
                module_path = os.path.splitext(module_path)[0]
                if module_path == '__init__':
                    # __init__.py in {root} does not have implementation
                    # so skip
                    continue
                if os.path.basename(module_path) == '__init__':
                    # 'foo/__init__.py' should be loaded as a module 'foo'
                    module_path = os.path.dirname(module_path)
                # Convert IO path to module path
                module_path = module_path.replace(os.sep, '.')
                yield (path, module_path)


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
    file_path = elem[1]
    if not exists(file_path):
        file_path = join(dirname(tagpath), elem[1])
    file_path = normpath(file_path)
    info = {
        'name': elem[0],
        'file': file_path,
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
                    r'([~.*\[\]\\])', r'\\\1',
                    re.sub(r'^/|/;"$', '', elem[2]))
        return info

    pattern = m.group(0)
    if re.match(r'\d+;"$', pattern):
        info['line'] = re.sub(r';"$', '', pattern)
    else:
        info['pattern'] = re.sub(r'([~.*\[\]\\])', r'\\\1',
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
