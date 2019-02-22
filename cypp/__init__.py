# [SublimeLinter @python:3]
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function, absolute_import


__version_info__ = (0, 2, 0)
__version__ = ".".join(str(x) for x in __version_info__)


FLAG_REPLACE = "#? "
FLAG_PREPEND = "#< "


def run(fpi, fpo):
    skip_next_line = False

    for i, line in enumerate(fpi):
        if i == 0 and line.startswith("#!"):
            if "3" in line:
                fpo.write("# cython: language_level=3\n")
            else:
                fpo.write("# cython: language_level=2\n")

            continue

        if line.lstrip().startswith(FLAG_REPLACE):
            line = line.replace(FLAG_REPLACE, "", 1)
            skip_next_line = True

        elif skip_next_line:
            skip_next_line = False
            continue

        elif FLAG_PREPEND in line:
            line, prepend = line.split(FLAG_PREPEND, 1)
            spaces = len(line) - len(line.lstrip())
            line = line[0:spaces] + prepend.strip() + " " + line[spaces:]

        fpo.write(line.rstrip())
        fpo.write("\n")
