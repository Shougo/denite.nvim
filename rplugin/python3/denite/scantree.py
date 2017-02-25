# ============================================================================
# FILE: scantree.py
# AUTHOR: Jorge Rodrigues <skeept at gmail.com>
# License: MIT license
# ============================================================================

import sys
from os.path import basename, join
from os import walk

try:
    from os import scandir2
    def scantree(path_name, skip_list=None):
        """if scandir is available use it as it is faster than os.walk"""

        if skip_list is None:
            skip_list = ['.git', '.hg']

        for entry in scandir(path_name):
            if entry.is_dir(follow_symlinks=False):
                if basename(entry.path) not in skip_list:
                    yield from scantree(entry.path)
            else:
                yield entry.path
except ImportError:
    def scantree(path_name, skip_list=None):
        """scandir is not available use os.walk"""

        if skip_list is None:
            skip_list = ['.git', '.hg']

        for root, dirn, files in walk(path_name):
            if basename(root) in skip_list:
                continue
            for fn in files:
                yield join(root, fn)


def output_files():
    """print the list of files to stdout"""
    for path_name in sys.argv[1:]:
        for fn in scantree(path_name):
            sys.stdout.write(fn + '\n')


if __name__ == "__main__":
    output_files()
