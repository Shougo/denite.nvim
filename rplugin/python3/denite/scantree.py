# ============================================================================
# FILE: scantree.py
# AUTHOR: Jorge Rodrigues <skeept at gmail.com>
# License: MIT license
# ============================================================================

import sys
from os.path import basename, join
from os import walk
import argparse
import fnmatch
import os
import time

DEFAULT_SKIP_LIST = ['.git', '.hg']


try:
    # 'scandir' was introduced at Python 3.5.
    # See https://pypi.python.org/pypi/scandir
    from os import scandir

    def scantree(path_name, skip_list=None):
        """This function returns the files present in path_name, including the
        files present in subfolders.

        Implementation uses scandir, if available, as it is faster than
        os.walk"""

        if skip_list is None:
            skip_list = DEFAULT_SKIP_LIST

        try:
            for entry in scandir(path_name):
                if is_ignored(entry.path, skip_list):
                    continue
                if entry.is_dir(follow_symlinks=False):
                    yield from scantree(entry.path, skip_list)
                else:
                    yield entry.path
        except PermissionError:
            yield ("PermissionError reading {}".format(path_name))

except ImportError:
    def scantree(path_name, skip_list=None):
        """This function returns the files present in path_name, including the
        files present in subfolders using os.walk"""

        if skip_list is None:
            skip_list = DEFAULT_SKIP_LIST

        for root, dirn, files in walk(path_name):
            if basename(root) in skip_list:
                continue
            for filename in files:
                yield join(root, filename)


def output_lines(lines):
    try:
        sys.stdout.write(''.join(lines))
        sys.stdout.flush()
    except UnicodeEncodeError:
        pass


def is_ignored(name, ignore_list):
    """checks if file name matches the ignore list"""
    return any(fnmatch.fnmatch(name, p) for p in ignore_list)


def output_files():
    """print the list of files to stdout"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, default=os.curdir,
                        help='path to look for the files')
    parser.add_argument('--ignore', type=str,
                        help='command separated list of patterns to ignore',
                        default='.hg,.git')

    args = parser.parse_args()
    ignore = args.ignore.split(',')
    # later we can account for more paths
    for path_name in [args.path]:
        curr_list = []
        max_size = 40
        max_time_without_write = 0.005
        last_write_time = time.time()
        for fn in scantree(path_name, ignore):
            curr_list.append(fn + '\n')
            if (len(curr_list) >= max_size or curr_list and
                    time.time() - last_write_time > max_time_without_write):
                output_lines(curr_list)
                curr_list = []
                last_write_time = time.time()

        if curr_list:
            output_lines(curr_list)


if __name__ == "__main__":
    output_files()
