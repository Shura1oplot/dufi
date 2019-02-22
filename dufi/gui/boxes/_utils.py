# [SublimeLinter @python:3]
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function, absolute_import

from contextlib import contextmanager

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk


@contextmanager
def ensure_parent(parent):
    has_parent = parent is not None

    if not has_parent:
        parent = tk.Tk()
        parent.withdraw()

    yield parent

    if not has_parent:
        parent.destroy()
