# [SublimeLinter @python:3]
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function, absolute_import

from tkinter import messagebox as _mbox

from .._utils import ensure_parent


def showinfo(title=None, message=None, **options):
    with ensure_parent(options.pop("parent", None)) as parent:
        return _mbox.showinfo(title, message, parent=parent, **options)


def showwarning(title=None, message=None, **options):
    with ensure_parent(options.pop("parent", None)) as parent:
        return _mbox.showwarning(title, message, parent=parent, **options)


def showerror(title=None, message=None, **options):
    with ensure_parent(options.pop("parent", None)) as parent:
        return _mbox.showerror(title, message, parent=parent, **options)


def askquestion(title=None, message=None, **options):
    with ensure_parent(options.pop("parent", None)) as parent:
        return _mbox.askquestion(title, message, parent=parent, **options)


def askokcancel(title=None, message=None, **options):
    with ensure_parent(options.pop("parent", None)) as parent:
        return _mbox.askokcancel(title, message, parent=parent, **options)


def askyesno(title=None, message=None, **options):
    with ensure_parent(options.pop("parent", None)) as parent:
        return _mbox.askyesno(title, message, parent=parent, **options)


def askyesnocancel(title=None, message=None, **options):
    with ensure_parent(options.pop("parent", None)) as parent:
        return _mbox.askyesnocancel(title, message, parent=parent, **options)


def askretrycancel(title=None, message=None, **options):
    with ensure_parent(options.pop("parent", None)) as parent:
        return _mbox.askretrycancel(title, message, parent=parent, **options)
