# [SublimeLinter @python:3]

import pyxlsb2


def read(fname, sheet=None):
    wb = pyxlsb2.open_workbook(fname)

    datemode = int(wb.props.date1904)

    def _f(ws):
        return ws.name.name, datemode, _rows_iter(ws)

    if sheet is None:
        yield _f(wb.get_sheet_by_index(0))

    elif hasattr(sheet, "match"):
        for ws in wb.sheets:
            if sheet.match(ws.name):
                yield _f(wb.get_sheet_by_name(ws.name))

    elif callable(sheet):
        result = sheet(wb.sheetnames)

        if isinstance(result, (tuple, int)):
            for name in result:
                yield _f(wb.get_sheet_by_name(name))

        elif isinstance(result, int):
            yield _f(wb.get_sheet_by_index(result))

        else:
            yield _f(wb.get_sheet_by_name(result))

    elif isinstance(sheet, int):
        yield _f(wb.get_sheet_by_index(sheet))

    else:
        yield _f(wb.get_sheet_by_name(sheet))


def _rows_iter(ws):
    for row in ws.rows():
        yield [x.date_value if x.is_date_formatted else x.value for x in row]


if __name__ == "__main__":
    pass
