# [SublimeLinter @python:3]
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function, absolute_import

import sys

if sys.version_info < (3,):
    from ._win32 import *
else:
    from ._tk import *
