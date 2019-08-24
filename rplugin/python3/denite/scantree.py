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
import typing

DEFAULT_SKIP_LIST = ['.git', '.hg']
SkipList = typing.Optional[typing.List[str]]


def scantree(
    path_name: str, skip_list: SkipList = None, types: str = 'f'
) -> typing.Generator[typing.Union[str, PermissionError], None, None]:
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
                if 'd' in types:
                    yield entry.path
                yield from scantree(entry.path, skip_list, types)
            elif 'f' in types:
                yield entry.path
    except PermissionError as exc:
        yield exc


def output_lines(out: typing.List[str], err: typing.List[str]) -> None:
    try:
        sys.stdout.write(''.join(out))
        sys.stdout.flush()
    except UnicodeEncodeError:
        pass
    try:
        sys.stderr.write(''.join(err))
        sys.stderr.flush()
    except UnicodeEncodeError:
        pass


def is_ignored(name: str, ignore_list: typing.List[str]) -> bool:
    """checks if file name matches the ignore list"""
    name = basename(name)
    return bool(any(fnmatch.fnmatch(name, p) for p in ignore_list))


def output_files() -> None:
    """print the list of files to stdout"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, default=curdir,
                        help='path to look for the files')
    parser.add_argument('--ignore', type=str,
                        help='command separated list of patterns to ignore',
                        default='.hg,.git')
    parser.add_argument('--type', type=str, nargs='*',
                        choices=['f', 'd'], default='f',
                        help='output file types')

    args = parser.parse_args()
    ignore = list(set(args.ignore.split(',')))
    types = ''.join(set(args.type))
    # later we can account for more paths
    for path_name in [args.path]:
        curr_outs = []
        curr_errs = []
        max_size = 40
        max_time_without_write = 0.005
        last_write_time = time.time()
        for name in scantree(path_name, ignore, types):
            if isinstance(name, str):
                curr_outs.append(name + '\n')
            elif isinstance(name, Exception):
                curr_errs.append(str(name) + '\n')
            if (max(len(curr_outs), len(curr_errs)) >= max_size
                or ((curr_outs or curr_errs) and
                    time.time() - last_write_time > max_time_without_write)):
                output_lines(curr_outs, curr_errs)
                curr_outs = []
                curr_errs = []
                last_write_time = time.time()

        if curr_outs or curr_errs:
            output_lines(curr_outs, curr_errs)


if __name__ == "__main__":
    output_files()
