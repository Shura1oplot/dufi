#!/usr/bin/env python3
# [SublimeLinter @python:3]

import sys
import os
import argparse

from . import dufi_commands, __version__


def main(argv=sys.argv):
    prog = os.path.basename(argv[0])
    parser = argparse.ArgumentParser(
        prog=prog,
        description=("Dump Fixer Tools are a set of useful utilities that helps "
                     "you to deal with rukozhopy data extractions. Please see "
                     "Data Assurance Wiki for details."),
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s v{}".format(__version__),
    )
    parser.set_defaults(command=None)

    subparsers = parser.add_subparsers(
        title="dufi commands",
    )

    for cmd in dufi_commands:
        cmd.add_args_parser_to(subparsers)

    args = parser.parse_args(argv[1:])

    if not args.command:
        parser.print_help()
        return 1

    return args.command(args)


if __name__ == "__main__":
    sys.exit(main())
