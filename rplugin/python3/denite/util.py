# ============================================================================
# FILE: util.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import json
import re
import os
import sys


def set_default(vim, var, val):
    return vim.call('denite#util#set_default', var, val)


def convert2list(expr):
    return (expr if isinstance(expr, list) else [expr])


def globruntime(vim, path):
    return vim.funcs.globpath(vim.options['runtimepath'], path, 1, 1)


def echo(vim, color, string):
    vim.call('denite#util#echo', color, string)


def debug(vim, expr):
    try:
        json_data = json.dumps(str(expr).strip())
    except Exception:
        vim.command('echomsg string(\'' + str(expr).strip() + '\')')
    else:
        vim.command('echomsg string(\'' + escape(json_data) + '\')')


def error(vim, msg):
    vim.call('denite#util#print_error', msg)


def escape(expr):
    return expr.replace("'", "''")


def fuzzy_escape(string, camelcase):
    # Escape string for python regexp.
    p = re.sub(r'([a-zA-Z0-9_])', r'\1.*', re.escape(string))
    if camelcase and re.search(r'[A-Z]', string):
        p = re.sub(r'([a-z])', (lambda pat:
                                '['+pat.group(1)+pat.group(1).upper()+']'), p)
    p = re.sub(r'([a-zA-Z0-9_])\.\*', r'\1[^\1]*', p)
    return p


def get_custom(custom, source_name, key, default):
    if source_name not in custom:
        return get_custom(custom, '_', key, default)
    elif key in custom[source_name]:
        return custom[source_name][key]
    elif key in custom['_']:
        return custom['_'][key]
    else:
        return default


def load_external_module(file, module):
    current = os.path.dirname(os.path.abspath(file))
    module_dir = os.path.join(os.path.dirname(current), module)
    sys.path.insert(0, module_dir)


def split_input(input):
    return [x for x in re.split(r'\s+', input) if x != '']
