# [SublimeLinter @python:3]

import sys
import os


def echo(*args, **kwargs):
    kwargs["flush"] = True
    # kwargs["file"] = sys.stderr
    print(*args, **kwargs)


def get_base_path():
    if getattr(sys, "frozen", False):
        prog_path = sys.executable
    else:
        prog_path = sys.argv[0]

    return os.path.dirname(os.path.abspath(prog_path))


def get_resources_path(*args):
    return os.path.join(get_base_path(), "resources", *args)
