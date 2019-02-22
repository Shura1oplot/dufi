# [SublimeLinter @python:3]
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function, absolute_import

import sys
import comtypes.client as cc
# import comtypes.gen.ShellObjects as sho
import comtypes.gen.ShellCoreObjects as sho


__all__ = ("Taskbar", )


class Taskbar(object):

    TBPF_NOPROGRESS = 0x0
    TBPF_INDETERMINATE = 0x1
    TBPF_NORMAL = 0x2
    TBPF_ERROR = 0x4
    TBPF_PAUSED = 0x8

    _taskbar = cc.CreateObject("{56FDF344-FD6D-11d0-958A-006097C9A090}",
                               interface=sho.ITaskbarList3)

    _states = {
        "no_progress": TBPF_NOPROGRESS,
        "indeterminate": TBPF_INDETERMINATE,
        "normal": TBPF_NORMAL,
        "error": TBPF_ERROR,
        "paused": TBPF_PAUSED,
    }

    def __init__(self, wnd):
        super(Taskbar, self).__init__()

        self.hwnd = int(wnd.wm_frame(), 16)
        self._last_status = None

    def ensure_progress_state(self, state):
        if self._last_status != state:
            self.set_progress_state(state)

    def set_progress_state(self, state):
        self._taskbar.HrInit()
        self._taskbar.SetProgressState(self.hwnd, self._states[state])
        self._last_status = state

    def set_progress_value(self, value, total=100):
        self._taskbar.HrInit()
        self._taskbar.SetProgressValue(self.hwnd, int(value), int(total))
