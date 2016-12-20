# ============================================================================
# FILE: util.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import re
import os
import sys
import glob


def set_default(vim, var, val):
    return vim.call('denite#util#set_default', var, val)


def convert2list(expr):
    return (expr if isinstance(expr, list) else [expr])


def globruntime(runtimepath, path):
    ret = []
    for rtp in re.split(',', runtimepath):
        ret += glob.glob(rtp + '/' + path)
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
    if hasattr(vim, 'err_write'):
        string = (expr if isinstance(expr, str) else str(expr))
        return vim.err_write('[denite] ' + string + '\n')
    else:
        vim.call('denite#util#print_error', expr)


def clear_cmdline(vim):
    vim.command('redraw | echo')


def escape(expr):
    return expr.replace("'", "''")


def escape_syntax(expr):
    return re.sub(r'([/~])', r'\\\1', expr)


def escape_fuzzy(string, camelcase):
    # Escape string for python regexp.
    p = re.sub(r'([a-zA-Z0-9_-])(?!$)', r'\1[^\1]*', string)
    if camelcase and re.search(r'[A-Z](?!$)', string):
        p = re.sub(r'([a-z])(?!$)',
                   (lambda pat: '['+pat.group(1)+pat.group(1).upper()+']'), p)
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


def load_external_module(file, module):
    current = os.path.dirname(os.path.abspath(file))
    module_dir = os.path.join(os.path.dirname(current), module)
    sys.path.insert(0, module_dir)


def split_input(input):
    return [x for x in re.split(r'\s+', input) if x != '']


def path2dir(path):
    return path if os.path.isdir(path) else os.path.dirname(path)


def path2project(vim, path):
    return vim.call('denite#util#path2project_directory', path)


def parse_jump_line(cwd, line):
    m = re.search(r'^(.*):(\d+)(?::(\d+))?:(.*)$', line)
    if not m or not m.group(1) or not m.group(4):
        return []

    if re.search(r':\d+$', m.group(1)):
        # Use column pattern
        m = re.search(r'^(.*):(\d+):(\d+):(.*)$', line)

    [path, linenr, col, text] = m.groups()

    if not linenr:
        linenr = '1'
    if not col:
        col = '0'
    if not os.path.isabs(path):
        path = cwd + '/' + path

    return [path, linenr, col, text]


def expand(path):
    return os.path.expandvars(os.path.expanduser(path))


def convert2fuzzy_pattern(input):
    return '\|'.join([escape_fuzzy(x, True) for x in split_input(input)])


def convert2regex_pattern(input):
    return '\|'.join(split_input(input))


def parse_command(array, **kwargs):
    def parse_arg(arg):
        if arg.startswith(':') and arg[1:] in kwargs:
            return kwargs[arg[1:]]
        return arg

    return [parse_arg(i) for i in array]


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
