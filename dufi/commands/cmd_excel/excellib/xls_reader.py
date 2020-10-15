# [SublimeLinter @python:3]

import datetime
import xlrd


def read(fname, sheet=None):
    book = xlrd.open_workbook(filename=fname)
    datemode = book.datemode
    sheet_names = []

    if hasattr(sheet, "match"):
        for sheet_name in book.sheet_names():
            if sheet.match(sheet_name):
                sheet_names.append(sheet_name)

    elif callable(sheet):
        sheet_names = sheet(book.sheet_names())

    else:
        sheet_names = [sheet, ]

    for sheet_name in sheet_names:
        if isinstance(sheet_name, str):
            worksheet = book.sheet_by_name(sheet_name)

        else:  # int or None
            worksheet = book.sheet_by_index(sheet_name or 0)

        yield worksheet.name, datemode, read_worksheet(worksheet, datemode)


def read_worksheet(worksheet, datemode):
    columns = []

    for i in range(worksheet.ncols):
        values = worksheet.col_values(i)
        types = worksheet.col_types(i)[1:]  # skip header

        excel_type = determine_excel_type(types)

        if excel_type == xlrd.biffh.XL_CELL_BOOLEAN:
            values = normalize_booleans(values)
        elif excel_type == xlrd.biffh.XL_CELL_DATE:
            values = normalize_dates(values, datemode)

        columns.append(values)

    if not columns:
        return []

    rows = []

    for i in range(len(columns[0])):
        rows.append([c[i] for c in columns])

    return rows


def determine_excel_type(types):
    """
    Determine the correct type for a column from a list of cell types.
    """
    types_set = set(types)
    types_set.discard(xlrd.biffh.XL_CELL_EMPTY)
    types_set.discard(xlrd.biffh.XL_CELL_ERROR)

    # Normalize mixed types to text
    if len(types_set) > 1:
        return xlrd.biffh.XL_CELL_TEXT

    try:
        return types_set.pop()
    except KeyError:
        return xlrd.biffh.XL_CELL_EMPTY


def normalize_booleans(values):
    normalized = []

    for value in values:
        if value is None or value == "":
            normalized.append(None)
        else:
            normalized.append(bool(value))

    return normalized


def normalize_dates(values, datemode=0):
    """
    Normalize a column of date cells.
    """
    normalized = []

    for v in values:
        if not v:
            normalized.append(None)
            continue

        if not isinstance(v, float):
            normalized.append(v)
            continue

        v_tuple = xlrd.xldate_as_tuple(v, datemode)

        if v_tuple[3:] == (0, 0, 0):
            # Date only
            normalized.append(datetime.date(*v_tuple[:3]))
        elif v_tuple[:3] == (0, 0, 0):
            normalized.append(datetime.time(*v_tuple[3:]))
        else:
            # Date and time
            normalized.append(datetime.datetime(*v_tuple))

    return normalized
