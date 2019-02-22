# [SublimeLinter @python:3]
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function, absolute_import

import tkinter.filedialog

from .._utils import ensure_parent


def fileopenbox(title=None, filetypes=(), initialdir=None, defaultextension=None,
                initialfile=None, multiple=False, message=None, parent=None):
    with ensure_parent(parent) as _parent:
        return tkinter.filedialog.askopenfilename(
            title=title,
            filetypes=filetypes,
            initialdir=initialdir,
            defaultextension=defaultextension,
            initialfile=initialfile,
            multiple=multiple,
            message=message,
            parent=_parent)


def filesavebox(title=None, filetypes=(), initialdir=None, defaultextension=None,
                initialfile=None, message=None, parent=None):
    with ensure_parent(parent) as _parent:
        return tkinter.filedialog.asksaveasfilename(
            title=title,
            filetypes=filetypes,
            initialdir=initialdir,
            defaultextension=defaultextension,
            initialfile=initialfile,
            message=message,
            parent=_parent)


def diropenbox(title=None, initialdir=None, parent=None, mustexist=True):
    with ensure_parent(parent) as _parent:
        return tkinter.filedialog.askdirectory(
            title=title,
            initialdir=initialdir,
            parent=_parent,
            mustexist=mustexist)
