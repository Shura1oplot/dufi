# [SublimeLinter @python:3]
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function, absolute_import

import os
import six
import pywintypes
import win32con
import win32gui


def _filebox(mode, title=None, filetypes=(), initialdir=None, defaultextension=None,
             initialfile=None, multiple=False, message=None, parent=None):
    kwargs = {}

    kwargs["MaxFile"] = 1024 ** 2

    if defaultextension:
        kwargs["DefExt"] = defaultextension

    if initialdir:
        kwargs["InitialDir"] = initialdir

    if initialfile:
        kwargs["File"] = initialfile

    if title:
        kwargs["Title"] = title

    open_flags = win32con.OFN_EXPLORER | win32con.OFN_HIDEREADONLY \
        | win32con.OFN_PATHMUSTEXIST

    if mode == "open":
        open_flags |= win32con.OFN_FILEMUSTEXIST
    else:
        open_flags |= win32con.OFN_OVERWRITEPROMPT

    if multiple:
        open_flags |= win32con.OFN_ALLOWMULTISELECT

    kwargs["Flags"] = open_flags

    all_files_filter = ("All Files (*.*)", "*.*")
    filter_parts = []

    for (name, mask) in filetypes:
        filter_parts.append(name)

        if isinstance(mask, six.string_types):
            mask = (mask, )

        filter_parts.append(";".join(mask))

    filter_parts.extend(all_files_filter)

    kwargs["CustomFilter"] = "\0".join(all_files_filter) + "\0"
    kwargs["Filter"] = "\0".join(filter_parts) + "\0"
    kwargs["FilterIndex"] = 0

    if parent:
        try:
            kwargs["hwndOwner"] = int(parent.wm_frame(), 16)
        except (AttributeError, ValueError):
            pass

    if mode == "open":
        func = win32gui.GetOpenFileNameW
    else:
        func = win32gui.GetSaveFileNameW

    try:
        fname, user_filter, flags = func(**kwargs)
    except pywintypes.error:
        return []

    if not multiple:
        return fname

    files = fname.split("\0")

    if len(files) == 1:
        return [files[0], ]

    return [os.path.join(files[0], x) for x in files[1:]]


def fileopenbox(*args, **kwargs):
    return _filebox("open", *args, **kwargs)


def filesavebox(*args, **kwargs):
    return _filebox("save", *args, **kwargs)


def diropenbox(title=None, initialdir=None, parent=None, mustexist=True):
    if not mustexist:
        raise NotImplementedError("mustexist must be True")

    kwargs = {}

    if initialdir:
        kwargs["InitialDir"] = initialdir

    kwargs["File"] = "Select Forlder"

    if title:
        kwargs["Title"] = title

    kwargs["Flags"] = win32con.OFN_EXPLORER | win32con.OFN_HIDEREADONLY \
        | win32con.OFN_PATHMUSTEXIST | win32con.OFN_NOVALIDATE

    # kwargs["CustomFilter"] = "Folder\0*..\0"
    kwargs["Filter"] = "Folder\0*..\0Folder (Show Files)\0*.*"
    kwargs["FilterIndex"] = 0

    if parent:
        try:
            kwargs["hwndOwner"] = int(parent.wm_frame(), 16)
        except (AttributeError, ValueError):
            pass

    try:
        fname, user_filter, flags = win32gui.GetOpenFileNameW(**kwargs)
    except win32gui.error:
        return None

    return os.path.dirname(fname)


if __name__ == "__main__":
    pass
    # print(fileopenbox(filetypes=(("Python files (*.py)", "*.py"), ), multiple=True))
    # import ctypes; ctypes.windll.user32.SetProcessDPIAware()
    # print(diropenbox("Choose folder with *.fil files"))
