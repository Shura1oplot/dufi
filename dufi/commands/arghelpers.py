# [SublimeLinter @python:3]

import sys
import os
from glob import glob

from ..utils import echo


class GUIOpt(object):

    def __init__(self, parser):
        super(GUIOpt, self).__init__()

        self.is_fake = isinstance(parser, FakeParser)

    def __call__(self, **kwargs):
        if self.is_fake:
            return {"gui_options": kwargs}
        else:
            return {}


class FakeParser(object):

    def __init__(self):
        super(FakeParser, self).__init__()

        self.command = None
        self.help = None
        self.args = []

    def add_parser(self, *args, **kwargs):
        return self

    def set_defaults(self, *args, **kwargs):
        pass

    def add_argument(self, short_arg, long_arg=None, *,
                     action="store",
                     choices=None,
                     default=None,
                     help="",
                     gui_options=None,
                     **_):
        if long_arg is None:
            short_arg, long_arg = None, short_arg

        spec = {}

        if gui_options is not None:
            spec.update(gui_options)

        if "action" not in spec and action in ("store_true", "store_false"):
            spec["action"] = "truefalse"

        if "default" not in spec and default:
            spec["default"] = default

        if "choices" not in spec and choices:
            spec["choices"] = choices

        self.args.append((long_arg, spec, help))


def type_single_byte(s):
    s = s.encode("ascii")

    if len(s) != 1:
        raise ValueError(s)

    b = s[0]

    if not isinstance(b, int):
        raise ValueError(repr(b))

    return b


def get_separator(args):
    if getattr(args, "tab_separator", False):
        sep = b"\t"[0]
    else:
        sep = args.separator

    if not isinstance(sep, int):
        raise ValueError(repr(sep))

    return sep


def format_file_path(mask, file):
    file_dir = os.path.dirname(file) or "."
    file_name = os.path.basename(file)
    file_root, file_ext = os.path.splitext(file_name)

    if file_ext.startswith("."):
        file_ext = file_ext[1:]

    if mask.count("!") in (1, 2):
        if mask.startswith("!"):
            return mask.replace("!", file_dir, 1) \
                       .replace("!", file_root, 1)
        else:
            return mask.replace("!", file_root, 1) \
                       .replace("!", file_ext, 1)

    return mask.replace("!", file_dir, 1) \
               .replace("!", file_root, 1) \
               .replace("!", file_ext, 1)


def process_files(args):
    files = get_files(args)

    for i, file in enumerate(files, 1):
        echo("Processing {}/{}: {}".format(i, len(files), os.path.basename(file)))
        yield file


def get_files(args, _cache={}):
    if "files" in _cache:
        return _cache["files"]

    files = []

    if args.list:
        for list_file in args.files:
            if list_file == "-":
                for file in sys.stdin:
                    files.append(file.strip())

            else:
                with open(list_file, "r") as fp:
                    for file in fp:
                        files.append(file.strip())

    else:
        for mask in args.files:
            for file in glob(mask):
                files.append(file.strip())

    result = []

    for file in files:
        if not os.path.exists(file):
            echo("WARNING: file not found:", file)
            continue

        if file in result:
            continue

        result.append(file)

    _cache["files"] = result
    return result
