# [SublimeLinter @python:3]
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function, absolute_import

import sys
import locale
import ctypes

try:
    from tkinter import ttk
except ImportError:
    import ttk


def set_system_encoding():
    if sys.version_info < (3,):
        reload(sys)
        sys.setdefaultencoding(locale.getpreferredencoding() or "utf-8")


def set_dpi_aware():
    if not getattr(sys, "frozen", False):
        ctypes.windll.user32.SetProcessDPIAware()


def fix_scaling_bug(root=None):
    user32 = ctypes.windll.user32

    if root:
        need_fix = user32.GetDpiForWindow(root.winfo_id()) > 150
    else:
        need_fix = user32.GetDpiForSystem() > 150

    if need_fix:
        ttk.Style().configure("Treeview", rowheight=28)
