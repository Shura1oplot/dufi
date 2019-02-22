# [SublimeLinter @python:3]
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function, absolute_import

import sys
import io

from . import run


def main(argv=sys.argv):
    with io.open(argv[1], "r", encoding="utf-8") as fpi, \
            io.open(argv[2], "w", encoding="utf-8") as fpo:
        return run(fpi, fpo)


if __name__ == "__main__":
    sys.exit(main())
