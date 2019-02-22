# [SublimeLinter @python:3]
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function, absolute_import

import threading
import win32api
import win32con
import win32gui


class drag_accept_files(object):

    def __init__(self, wnd, callback):
        super(drag_accept_files, self).__init__()

        self.callback = callback
        self.hwnd = int(wnd.wm_frame(), 16)
        self._old_wnd_proc = win32gui.SetWindowLong(
            self.hwnd, win32con.GWL_WNDPROC, self._new_wnd_proc)
        self.accept_files = True

    @property
    def accept_files(self):
        raise NotImplementedError()

    @accept_files.setter
    def accept_files(self, value):
        win32gui.DragAcceptFiles(self.hwnd, bool(value))

    def _new_wnd_proc(self, hwnd, msg, wparam, lparam):
        assert self.hwnd == hwnd

        if msg == win32con.WM_DROPFILES:
            files = []

            for i in range(win32api.DragQueryFile(wparam)):
                files.append(win32api.DragQueryFile(wparam, i))

            if files:
                threading.Thread(target=self.callback, args=(files, )).start()

        if msg == win32con.WM_DESTROY:
            win32api.SetWindowLong(hwnd, win32con.GWL_WNDPROC, self._old_wnd_proc)

        return win32gui.CallWindowProc(self._old_wnd_proc, hwnd, msg, wparam, lparam)
