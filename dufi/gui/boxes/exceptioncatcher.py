# [SublimeLinter @python:3]
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function, absolute_import

import sys

from .custombox import exceptionbox


class TkExceptionCatcher(object):

    root = None

    def __init__(self, func, subst, widget):
        super().__init__()

        self.func = func
        self.subst = subst
        self.widget = widget

    def __call__(self, *args):
        try:
            if self.subst:
                args = self.subst(*args)

            return self.func(*args)

        except SystemExit:
            raise

        except:
            if self.root:
                self.root.destroy()

            exceptionbox()
            sys.exit(1)
