# [SublimeLinter @python:3]

import sys
import os
from glob import glob

from .utils import colno
from .converter import ExcelConverter, StopConverting


__version_info__ = (0, 5, 0)
__version__ = ".".join(str(x) for x in __version_info__)


if sys.version_info < (3, 3):
    raise RuntimeError("python >= 3.3 is required")


_converters = []


class ConverterMeta(type):

    def __new__(metacls, name, bases, namespace, **kwds):
        cls = super().__new__(metacls, name, bases, namespace, **kwds)

        if cls.sheet_pattern and not cls.disable:
            _converters.append(
                ExcelConverter(cls(),
                               sheet_pattern=cls.sheet_pattern,
                               output_file_mask=cls.output_file_mask,
                               row_start=cls.row_start,
                               row_stop=cls.row_stop,
                               last_column=cls.last_column,
                               max_size_default=cls.max_size_default,
                               max_size_custom=cls.max_size_custom,
                               last_cell_limit=cls.last_cell_limit))

        return cls


class Converter(object, metaclass=ConverterMeta):

    sheet_pattern = None
    output_file_mask = None
    disable = False

    row_start = 0
    row_stop = 0
    last_column = None
    max_size_default = None
    max_size_custom = None
    last_cell_limit = None

    def __call__(self, row, row_no):
        return self.convert(row, row_no)

    def convert(self, row, row_no):
        return row


def sheet(sheet_pattern, output_file_mask, disable=False, **kwargs):
    if disable:
        return lambda func: func

    def decorator(func):
        conv = ExcelConverter(func, sheet_pattern, output_file_mask, **kwargs)
        _converters.append(conv)
        return func

    return decorator


def run(project_path, *args):
    project_path = os.path.abspath(project_path)

    for mask in args:
        for file_path in glob(os.path.join(project_path, mask)):
            if not os.path.isfile(file_path):
                continue

            print(os.path.basename(file_path))

            for convert in _converters:
                convert(file_path)
