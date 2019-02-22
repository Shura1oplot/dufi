# [SublimeLinter @python:3]

from xlsxwriter.utility import xl_cell_to_rowcol


def colno(s):
    if not s.isalpha():
        raise ValueError(s)

    return xl_cell_to_rowcol(s.upper() + "1")[1]
