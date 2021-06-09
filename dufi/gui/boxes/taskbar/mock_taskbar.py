# [SublimeLinter @python:3]
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function, absolute_import


__all__ = ("Taskbar", )


class Taskbar(object):

    def __init__(self, wnd):
        super().__init__()

    def ensure_progress_state(self, state):
        pass

    def set_progress_state(self, state):
        pass

    def set_progress_value(self, value, total=100):
        pass
