# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function, absolute_import

import os
import io
import subprocess

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

from ..pygubuapp import GUIApplication

from .logboxui import logboxui


__all__ = ("logbox", )


class LogDialogBox(GUIApplication):

    title = "Application Log"

    ui_content = logboxui

    def __init__(self, master, logfile, title=None):
        super(LogDialogBox, self).__init__(master)

        self.logfile = logfile

        if title:
            self.title = title

        w = self.builder.get_object("TextLogContent")
        w.delete(1.0, tk.END)
        w.insert(1.0, io.open(logfile).read().rstrip())
        w.update()
        w.see(tk.END)
        w.focus()

    def on_button_locate(self, event=None):
        if not os.path.isfile(self.logfile):
            return

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        subprocess.Popen(
            'explorer /select,"{}"'.format(self.logfile).encode("cp1251"),
            shell=True, startupinfo=startupinfo)


def logbox(logfile, title=None, parent=None):
    root = None

    if not parent:
        root = tk.Tk()
        root.withdraw()
        parent = root

    LogDialogBox(parent, logfile, title)

    if root:
        root.mainloop()


if __name__ == "__main__":
    pass
