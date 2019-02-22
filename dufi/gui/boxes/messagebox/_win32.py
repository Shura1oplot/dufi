# [SublimeLinter @python:3]
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function, absolute_import

import win32gui
import win32con


_mb_flags = {"info":  win32con.MB_ICONINFORMATION,
             "warn":  win32con.MB_ICONWARNING,
             "error": win32con.MB_ICONERROR}


def _messagebox(msgtype, title, message, parent):
    try:
        hwnd = int(parent.wm_frame(), 16)
    except (AttributeError, ValueError):
        hwnd = 0

    win32gui.MessageBox(hwnd, message or "", title or "", _mb_flags[msgtype])


def showinfo(title, message, parent=None, **kwargs):
    return _messagebox("info", title, message, parent)


def showwarning(title, message, parent=None, **kwargs):
    return _messagebox("warn", title, message, parent)


def showerror(title, message, parent=None, **kwargs):
    return _messagebox("error", title, message, parent)


def askquestion(*args, **kwargs):
    # tkMessageBox.askquestion
    raise NotImplementedError()


def askokcancel(*args, **kwargs):
    # tkMessageBox.askokcancel
    raise NotImplementedError()


def askyesno(*args, **kwargs):
    # tkMessageBox.askyesno
    raise NotImplementedError()


def askretrycancel(*args, **kwargs):
    # tkMessageBox.askretrycancel
    raise NotImplementedError()
