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

from glob import glob
from os.path import normpath, normcase, join, dirname, exists


def set_default(vim, var, val):
    return vim.call('denite#util#set_default', var, val)


def convert2list(expr):
    return (expr if isinstance(expr, list) else [expr])


def globruntime(runtimepath, path):
    ret = []
    for rtp in re.split(',', runtimepath):
        ret += glob(rtp + '/' + path)
    return ret


def echo(vim, color, string):
    vim.call('denite#util#echo', color, string)


def debug(vim, expr):
    if hasattr(vim, 'out_write'):
        string = (expr if isinstance(expr, str) else str(expr))
        return vim.out_write('[denite] ' + string + '\n')
    else:
        print(expr)


def error(vim, expr):
    string = (expr if isinstance(expr, str) else str(expr))
    vim.call('denite#util#print_error', string)


def clear_cmdline(vim):
    vim.command('redraw | echo')


def escape(expr):
    return expr.replace("'", "''")


def regex_convert_str_vim(string):
    return re.sub(r'([\^$.*\\/~\[\]])', r'\\\1', string)


def regex_convert_py_vim(expr):
    return r'\v' + re.sub(r'(?!\\)([/~])', r'\\\1', expr)


def escape_fuzzy(string):
    # Escape string for python regexp.
    p = re.sub(r'([a-zA-Z0-9_-])(?!$)', r'\1[^\1]*', string)
    p = re.sub(r'/(?!$)', r'/[^/]*', p)
    return p


def get_custom_source(custom, source_name, key, default):
    source = custom['source']
    if source_name not in source:
        return get_custom_source(custom, '_', key, default)
    elif key in source[source_name]:
        return source[source_name][key]
    elif key in source['_']:
        return source['_'][key]
    else:
        return default


def load_external_module(base, module):
    current = os.path.dirname(os.path.abspath(base))
    module_dir = join(os.path.dirname(current), module)
    sys.path.insert(0, module_dir)


def split_input(text):
    return [x for x in re.split(r'\s+', text) if x != ''] if text else ['']


def path2dir(path):
    return path if os.path.isdir(path) else os.path.dirname(path)


def path2project(vim, path, root_markers):
    return vim.call('denite#project#path2project_directory',
                    path, root_markers)


def parse_jump_line(path_head, line):
    m = re.search(r'^((?:[a-zA-Z]:)?[^:]*):(\d+)(?::(\d+))?:(.*)$', line)
    if not m or not m.group(1) or not m.group(4):
        return []

    if re.search(r':\d+$', m.group(1)):
        # Use column pattern
        m = re.search(r'^((?:[a-zA-Z]:)?[^:]*):(\d+):(\d+):(.*)$', line)

    [path, linenr, col, text] = m.groups()

    if not linenr:
        linenr = '1'
    if not col:
        col = '0'
    if not os.path.isabs(path):
        path = join(path_head, path)

    return [path, linenr, col, text]


def expand(path):
    return os.path.expandvars(os.path.expanduser(path))


def abspath(vim, path):
    return normpath(join(vim.call('getcwd'), expand(path)))


def relpath(vim, path):
    return normpath(vim.call('fnamemodify', expand(path), ':~:.'))


def convert2fuzzy_pattern(text):
    def esc(string):
        # Escape string for convert2fuzzy_pattern.
        p = re.sub(r'([a-zA-Z0-9_-])(?!$)', r'\1[^\1]{-}', string)
        p = re.sub(r'/(?!$)', r'/[^/]*', p)
        return p
    return '|'.join([esc(x) for x in split_input(text)])


def convert2regex_pattern(text):
    return '|'.join(split_input(text))


def parse_command(array, **kwargs):
    def parse_arg(arg):
        if arg.startswith(':') and arg[1:] in kwargs:
            return kwargs[arg[1:]]
        return arg

    return [parse_arg(i) for i in array]


# XXX: It override the builtin 'input()' function.
def input(vim, context, prompt='', text='', completion=''):
    try:
        if completion != '':
            return vim.call('input', prompt, text, completion)
        else:
            return vim.call('input', prompt, text)
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


def find_rplugins(context, source, loaded_paths):
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


def import_rplugins(name, context, source, loaded_paths):
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
        spec.loader.exec_module(module)
        if (not hasattr(module, name) or
                inspect.isabstract(getattr(module, name))):
            continue
        yield (getattr(module, name), path, module_path)


def parse_tagline(line, tagpath):
    elem = line.split("\t")
    file_path = elem[1]
    if not exists(file_path):
        file_path = normpath(join(dirname(tagpath), elem[1]))
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


def clearmatch(vim):
    if vim.call('exists', 'w:denite_match_id'):
        vim.call('matchdelete',
                 vim.current.window.vars['denite_match_id'])
        vim.command('unlet w:denite_match_id')
