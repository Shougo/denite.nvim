# ============================================================================
# FILE: scantree.py
# AUTHOR: Jorge Rodrigues <skeept at gmail.com>
# License: MIT license
# ============================================================================

import sys
from os.path import basename, join
from os import walk


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

        for entry in scandir(path_name):
            if entry.is_dir(follow_symlinks=False):
                if basename(entry.path) not in skip_list:
                    for path in scantree(entry.path):
                        yield path
            else:
                yield entry.path
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


def output_files():
    """print the list of files to stdout"""
    for path_name in sys.argv[1:]:
        for fn in scantree(path_name):
            sys.stdout.write(fn + '\n')


if __name__ == "__main__":
    output_files()
