#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function, absolute_import

import sys
import os
import threading
import warnings
import locale
import logging

import win32api
import win32con
import win32gui
import win32ts


PY2 = sys.version_info < (3,)

if PY2:
    reload(sys)
    sys.setdefaultencoding(locale.getpreferredencoding() or "utf-8")


NIN_BALLOONSHOW      = win32con.WM_USER + 2
NIN_BALLOONHIDE      = win32con.WM_USER + 3
NIN_BALLOONTIMEOUT   = win32con.WM_USER + 4
NIN_BALLOONUSERCLICK = win32con.WM_USER + 5
WM_TRAY_EVENT        = win32con.WM_USER + 20


win32gui.InitCommonControls()


class BalloonTooltip(object):

    def __init__(self, title, message, icon_type, callback):
        super(BalloonTooltip, self).__init__()

        self.title = title
        self.message = message
        self.icon_type = icon_type
        self.callback = callback

        self._class_atom = None
        self._hwnd = None
        self._hinst = None

    def show(self):
        # Register the Window class.
        wc = win32gui.WNDCLASS()
        self._hinst = wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = (bytes if PY2 else str)("PythonTaskbar")
        wc.lpfnWndProc = {win32con.WM_DESTROY: self._on_destroy,
                          WM_TRAY_EVENT: self._on_tray_event}
        self._class_atom = win32gui.RegisterClass(wc)

        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self._hwnd = win32gui.CreateWindow(
            self._class_atom, "Taskbar", style, 0, 0, win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT, 0, 0, self._hinst, None)
        win32gui.UpdateWindow(self._hwnd)
        win32ts.WTSRegisterSessionNotification(
            self._hwnd, win32ts.NOTIFY_FOR_THIS_SESSION)

        icon_path_name = self._find_icon()
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE

        try:
            hicon = win32gui.LoadImage(
                self._hinst, icon_path_name, win32con.IMAGE_ICON, 0, 0, icon_flags)
        except Exception:
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        # http://docs.activestate.com/activepython/3.2/pywin32/PyNOTIFYICONDATA.html
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self._hwnd, 0, flags, WM_TRAY_EVENT, hicon, "tooltip")
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)

        flags = {"error": win32gui.NIIF_ERROR,
                 "warn": win32gui.NIIF_WARNING,
                 "info": win32gui.NIIF_INFO}.get(self.icon_type, win32gui.NIIF_NONE)
        nid = (self._hwnd, 0, win32gui.NIF_INFO, WM_TRAY_EVENT, hicon,
               "Balloon tooltip", self.message, 200, self.title, flags)
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, nid)

        logging.debug("show(...) -> hwnd=%d", self._hwnd)

        win32gui.PumpMessages()

    def hide(self):
        if not self._hwnd:
            return

        win32gui.PostMessage(self._hwnd, WM_TRAY_EVENT, 0, NIN_BALLOONHIDE)

    def _find_icon(self):
        getattr(sys, '_MEIPASS', None)

        if getattr(sys, "frozen", False):
            base_path = getattr(sys, '_MEIPASS', None)

            if not base_path:
                base_path = os.path.dirname(sys.executable)

        else:
            base_path = os.path.dirname(sys.argv[0])

        return os.path.abspath(os.path.join(base_path, "balloontip.ico"))

    def _on_destroy(self, hwnd, msg, wparam, lparam):
        logging.debug("_on_destroy(hwnd=%d)", hwnd)

        if self._hwnd != hwnd:
            warnings.warn("_on_destroy called with invalid hwnd")
            return

        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, (hwnd, 0))
        win32gui.PostMessage(hwnd, win32con.WM_QUIT, 0, 0)
        self._hwnd = None

    def _on_tray_event(self, hwnd, msg, wparam, lparam):
        logging.debug("_on_tray_event(hwnd=%r, lparam=%s)", hwnd,
                      self._get_const_name(lparam))

        if self._hwnd != hwnd:
            warnings.warn("_on_tray_event called with invalid hwnd")
            return

        if lparam in (NIN_BALLOONHIDE, NIN_BALLOONTIMEOUT, NIN_BALLOONUSERCLICK,
                      win32con.WM_LBUTTONDOWN, win32con.WM_LBUTTONUP,
                      win32con.WM_LBUTTONDBLCLK, win32con.WM_RBUTTONDOWN,
                      win32con.WM_RBUTTONUP, win32con.WM_RBUTTONDBLCLK):
            logging.debug("_on_tray_event(...) -> destroy window")
            win32gui.DestroyWindow(hwnd)
            logging.debug("_on_tray_event(...) -> unregister class")
            win32gui.UnregisterClass(self._class_atom, self._hinst)
            self._class_atom = None
            self._hinst = None

        if lparam == NIN_BALLOONUSERCLICK and callable(self.callback):
            logging.debug("_on_tray_event(...) -> execute callback")
            self.callback()

    @staticmethod
    def _get_const_name(value, _cache={512: "WM_MOUSEMOVE"}):
        if value in _cache:
            return _cache[value]

        for var_name, var_value in globals().items():
            if var_name.startswith("NIN_") and var_value == value:
                _cache[value] = var_name
                return var_name

        for var_name in dir(win32con):
            if var_name.startswith("WM_") and getattr(win32con, var_name) == value:
                _cache[value] = var_name
                return var_name

        _cache[value] = str(value)
        return _cache[value]


def balloon_tip(title, message, *, icon_type=None, callback=None, block=True):
    wbt = BalloonTooltip(title, message, icon_type, callback)

    if block:
        wbt.show()
        return

    t = threading.Thread(target=wbt.show)
    t.daemon = True
    t.start()

    def hide_balloon_tip():
        wbt.hide()
        t.join()

    return t.is_alive, hide_balloon_tip


################################################################################


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    def _test_async():
        import time

        i = 0
        f = lambda: False

        while True:
            if not f():
                f, _ = balloon_tip("Example 3",
                                   "Async balloontip: {}".format(i),
                                   block=False)
                i += 1

            time.sleep(0.5)

    _test_async()
