# ============================================================================
# FILE: scantree.py
# AUTHOR: Jorge Rodrigues <skeept at gmail.com>
# License: MIT license
# ============================================================================

import sys
from os import curdir, scandir
from os.path import basename
import argparse
import fnmatch
import time

DEFAULT_SKIP_LIST = ['.git', '.hg']


def scantree(path_name, skip_list=None):
    """This function returns the files present in path_name, including the
    files present in subfolders.

    Implementation uses scandir, if available, as it is faster than
    os.walk"""

    if skip_list is None:
        skip_list = DEFAULT_SKIP_LIST

    try:
        for entry in (e for e in scandir(path_name)
                      if not is_ignored(e.path, skip_list)):
            if entry.is_dir(follow_symlinks=False):
                yield from scantree(entry.path, skip_list)
            else:
                yield entry.path
    except PermissionError:
        yield f'PermissionError reading {path_name}'


def output_lines(lines):
    try:
        sys.stdout.write(''.join(lines))
        sys.stdout.flush()
    except UnicodeEncodeError:
        pass


def is_ignored(name, ignore_list):
    """checks if file name matches the ignore list"""
    name = basename(name)
    return any(fnmatch.fnmatch(name, p) for p in ignore_list)


def output_files():
    """print the list of files to stdout"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, default=curdir,
                        help='path to look for the files')
    parser.add_argument('--ignore', type=str,
                        help='command separated list of patterns to ignore',
                        default='.hg,.git')

    args = parser.parse_args()
    ignore = list(set(args.ignore.split(',')))
    # later we can account for more paths
    for path_name in [args.path]:
        curr_list = []
        max_size = 40
        max_time_without_write = 0.005
        last_write_time = time.time()
        for name in scantree(path_name, ignore):
            curr_list.append(name + '\n')
            if (len(curr_list) >= max_size or curr_list and
                    time.time() - last_write_time > max_time_without_write):
                output_lines(curr_list)
                curr_list = []
                last_write_time = time.time()

        if curr_list:
            output_lines(curr_list)


if __name__ == "__main__":
    output_files()
