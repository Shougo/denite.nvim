import sys
import os


def scantree(pathn):
    """Use scandir if available else os.walk. scandir is supposed to be much faster"""
    
    skip_list = ['.git']

    if 'scandir' in dir(os):
        for entry in os.scandir(pathn):
            if entry.is_dir(follow_symlinks=False):
                if os.path.basename(entry.path) not in skip_list:
                    yield from scantree(entry.path)
            else:
                yield entry.path
    else:
        for root, dirn, files in os.walk(pathn):
            if os.path.basename(root) in skip_list:
                continue
            for fn in files:
                yield os.path.join(root, fn)


if __name__ == "__main__":
    for pathn in sys.argv[1:]:
        for fn in scantree(pathn):
            sys.stdout.write(fn + '\n')
