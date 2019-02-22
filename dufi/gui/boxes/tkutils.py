# [SublimeLinter @python:3]
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function, absolute_import


def center(window, master=None):
    (master or window).eval("tk::PlaceWindow {} center".format(
        window.winfo_toplevel()))
    # (master or window).eval("tk::PlaceWindow {} center".format(
    #     window.winfo_pathname(window.winfo_id())))
