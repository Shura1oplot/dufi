# [SublimeLinter @python:3]

import os
from itertools import chain
from datetime import datetime
import locale
import re

from .utils import colno
from .xlsx_reader import read as read_xlsx
from .xls_reader import read as read_xls
from .xlsb_reader import read as read_xlsb


ENCODING = locale.getpreferredencoding()


class StopConverting(Exception):
    pass


class ExcelConverter():

    def __init__(self,
                 callback,
                 sheet_mask,
                 file_mask,
                 row_start=0,
                 row_stop=0,
                 header_str=None,
                 find_header_limit=10,
                 last_column=None,
                 max_len_default=None,
                 max_len_custom=None,
                 last_cell_limit=None):
        super().__init__()

        self._callback = callback
        self._sheet_regex = self._make_regex(sheet_mask)
        self._file_mask = file_mask

        self._row_start = row_start or 0
        self._row_stop = row_stop or 0

        self._header_str = header_str
        self._find_header_limit = find_header_limit or 10

        if isinstance(last_column, str):
            self._column_count = colno(last_column) + 1
        else:
            self._column_count = last_column

        self._max_len_default = max_len_default
        self._max_len_custom = {(colno(k) if isinstance(k, str) else k): v
                                for k, v in (max_len_custom or {}).items()
                                if not isinstance(k, int) or k > 0}

        self._last_cell_limit = last_cell_limit

    def __call__(self, file_excel):
        file_out = self._format_file_path(file_excel, self._file_mask)

        excel_file_path = os.path.relpath(file_excel)

        if excel_file_path.startswith("..\\"):
            excel_file_path = os.path.abspath(file_excel)

        file_type = self._detect_file_type(file_excel)

        last_cell_limit = self._last_cell_limit and file_type != "xls"

        if file_type == "xls":
            read_excel = read_xls
        elif file_type == "xlsb":
            read_excel = read_xlsb
        else:  # xlsx. xlsm
            read_excel = read_xlsx

        os.makedirs(os.path.dirname(file_out), exist_ok=True)

        with open(file_out, "w", encoding=ENCODING, errors="replace") as fpo:
            for sheet_name, datemode, rows in read_excel(file_excel, self._sheet_regex):
                if last_cell_limit:
                    rows = self._last_cell_iter(rows, self._last_cell_limit)

                extra = (excel_file_path, str(datemode), sheet_name)
                self._write_sheet(fpo, rows, extra)

    def _detect_file_type(self, file):
        _, file_ext = os.path.splitext(file)
        file_ext = file_ext.lstrip(".").lower()

        if file_ext not in ("xls", "xlsx", "xlsm", "xlsb"):
            raise ValueError("unsupported file type: {}".format(file))

        with open(file, "rb") as fp:
            sig = fp.read(8)

        if sig == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
            file_type = "xls"

        elif sig[:4] == b"\x50\x4b\x03\x04":
            file_type = "xlsx"

        else:
            raise ValueError("unsupported file type: {}".format(file))

        if file_ext == file_type:
            return file_ext

        if file_type == "xls":
            return "xls"

        if file_ext in ("xlsb", "xlsm"):
            return file_ext

        return file_type

    def _write_sheet(self, fpo, rows, extra=()):
        header_found = False
        header_buf = []

        if not self._header_str:
            header_found = True

        for i, row in enumerate(rows, 1):
            if i < self._row_start:
                continue

            if self._column_count:
                while len(row) < self._column_count:
                    row.append("")

                row = row[:self._column_count]

            try:
                row = self._callback(row, i)
            except StopConverting:
                break

            if not row:
                continue

            row = list(chain(extra, (str(i), ), (self._conv_value(x) for x in row)))

            if self._max_len_default:
                row = [field[:self._max_len_custom.get(i, self._max_len_default)]
                       for i, field in enumerate(row, -len(extra)-1)]

            row_str = "\t".join(row) + "\n"

            if not header_found:
                if self._header_str in row_str:
                    header_found = True

                elif self._find_header_limit == i:
                    for row_str in header_buf:
                        fpo.write(row_str)

                    header_buf.clear()

                    header_found = True

            if header_found:
                fpo.write(row_str)
            else:
                header_buf.append(row_str)

            if self._row_stop == i:
                break

        if not header_found:
            for row_str in header_buf:
                fpo.write(row_str)

    @staticmethod
    def _make_regex(sheet_names):
        if not isinstance(sheet_names, (tuple, list)):
            sheet_names = [sheet_names, ]

        parts = []

        for sheet_name in sheet_names:
            parts.append("".join(r".*" if x == "*" else re.escape(x)
                                 for x in re.split(r"(\*)", sheet_name)))

        rex = "^({})$".format("|".join(parts))
        return re.compile(rex, flags=re.U | re.I)

    @staticmethod
    def _format_file_path(file, mask):
        file_dir = os.path.dirname(file) or "."
        file_name = os.path.basename(file)
        file_root, file_ext = os.path.splitext(file_name)

        if file_ext.startswith("."):
            file_ext = file_ext[1:]

        if mask.count("!") in (1, 2):
            if mask.startswith("!"):
                return mask.replace("!", file_dir, 1) \
                           .replace("!", file_root, 1)
            else:
                return mask.replace("!", file_root, 1) \
                           .replace("!", file_ext, 1)

        return mask.replace("!", file_dir, 1) \
                   .replace("!", file_root, 1) \
                   .replace("!", file_ext, 1)

    @staticmethod
    def _last_cell_iter(rows_iter, max_count):
        last_row = None
        count = 0

        for row in rows_iter:
            if row == last_row:
                count += 1

                if count > max_count:
                    break

            else:
                count = 0

            last_row = row
            yield row

    @staticmethod
    def _conv_value(value):
        if value is None:
            return ""

        elif isinstance(value, bytes):
            value = value.decode(ENCODING)

        elif isinstance(value, datetime):
            value = value.strftime("%Y-%m-%d %H:%M")

        elif isinstance(value, float):
            if value % 1 == 0:
                value = int(value)

            value = str(value)

        elif not isinstance(value, str):
            value = str(value)

        return value.replace("\n", " ").replace("\t", " ").strip()
