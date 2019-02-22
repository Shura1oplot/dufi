# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function, absolute_import

import traceback
from six import StringIO

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

from ..pygubuapp import GUIApplication
from .exceptionboxui import exceptionboxui


__all__ = ("exceptionbox", )


class ExceptionDialogBox(GUIApplication):

    title = "Application Error"

    ui_content = exceptionboxui

    def __init__(self, master, text, title=None):
        super(ExceptionDialogBox, self).__init__(master)

        if title:
            self.title = title

        self.init()

        w = self.builder.get_object("TextException")
        w.delete(1.0, tk.END)
        w.insert(1.0, text.rstrip())
        w.update()
        w.see(tk.END)
        w.focus()


def exceptionbox(title=None, parent=None):
    fp = StringIO()
    traceback.print_exc(file=fp)
    text = fp.getvalue()
    fp.close()

    if text == "None\n":
        return

    root = None

    if not parent:
        root = tk.Tk()
        root.withdraw()
        parent = root

    ExceptionDialogBox(parent, text, title)

    if root:
        root.mainloop()


if __name__ == "__main__":
    try:
        raise ValueError("atata")
    except:
        exceptionbox()
