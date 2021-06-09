# [SublimeLinter @python:3]
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function, absolute_import

import sys


try:
    from .real_taskbar import Taskbar
except ModuleNotFoundError:
    from .mock_taskbar import Taskbar
    print("WARNING: cannot load taskbar extension", file=sys.stderr)


__all__ = ("Taskbar", )
