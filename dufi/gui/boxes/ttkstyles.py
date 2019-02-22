# [SublimeLinter @python:3]
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function, absolute_import

try:
    from tkinter import ttk
    from tkinter import font as tk_font
except ImportError:
    import ttk
    import tkFont as tk_font


_ttk_styles = set()
_ttk_style_customizers = set()


def create_ttk_styles():
    for func in _ttk_style_customizers:
        func()


def _ttk_style_customizer(func):
    _ttk_style_customizers.add(func)

    def wrapper():
        if func.__name__ not in _ttk_styles:
            func()
            _ttk_styles.add(func.__name__)

    return wrapper


@_ttk_style_customizer
def create_ttk_style_white_frame():
    ttk.Style().configure("WhiteFrame.TFrame", background="White")
    ttk.Style().configure("WhiteLabel.TLabel", background="White")
    ttk.Style().configure("WhiteCheckbutton.TCheckbutton", background="White")


@_ttk_style_customizer
def create_ttk_style_plain_notebook():
    s = ttk.Style()
    s.configure("Plain.TNotebook", borderwidth=0)
    s.layout("Plain.TNotebook.Tab", [])


@_ttk_style_customizer
def create_ttk_style_bold_label():
    bold_font = tk_font.nametofont("TkDefaultFont").copy()
    bold_font.config(weight="bold")
    ttk.Style().configure("Bold.TLabel", font=bold_font)
    ttk.Style().configure("WhiteLabelBold.TLabel", font=bold_font, background="White")
