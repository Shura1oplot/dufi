# [SublimeLinter @python:3]

import re

from .excellib.converter import ExcelConverter

from ..base import Command, InvalidCommandArgs
from ..arghelpers import process_files


class ScriptCommand(Command):

    cli_command = "excel-to-csv"
    cli_command_aliases = ("xl2csv", )
    cli_command_help = "batch convert of Excel spreadsheets into CSV files"

    gui_order = 10
    gui_command = "Excel to CSV"
    gui_description = "Convert Excel spreadsheets to CSV files."
    gui_files_info_label_id = "LabelExcelFilesInfo"
    gui_info_message_widget = "MessageExcelInfo"

    gui_variables = ("excel_sheet", "excel_output", "excel_row_start", "excel_row_stop",
                     "excel_last_column", "excel_length_limit", "excel_truncate_1k",
                     "excel_truncate_4k", "excel_fix_data_range")

    gui_help_tooltips = {

        "LabelExcelOutputWarning": """
Output files will not be merged but rewritten!
Use "Convert & Merge" command to merge CSV files.
""",

        "LabelExcelSheetHelp": """
Specify sheet name or name mask ('*' can be used for matching any substring).
""",

        "LabelExcelOutputHelp": """
Each ! will be replaced by a part of the full file path:
1st ! - directory, 2nd ! - name w/o extension, 3rd ! - file extension
For example, we are going to process: 'C:\\JET\\journal_entries.csv'.
With mask '!\\!_NEW.!' output file will be 'C:\\JET\\journal_entries_NEW.csv'.
With mask '!\\NEW\\!.!' output file will be 'C:\\JET\\NEW\\journal_entries.csv.
""",

        "LabelExcelRowStartHelp": """
Start converting sheet from N row (skip N-1 first rows).
""",

        "LabelExcelRowStopHelp": """
Stop converting sheet reaching N row.
""",

        "LabelExcelLastColumnHelp": """
While converting ignore data after this column.
""",

        "LabelExcelLengthLimitHelp": """
Limit length of each value by maximum length specified.
If length of value is greater, it will be truncated.
""",

        "LabelExcelTruncate1kHelp": """
Specify column names (divided by a comma) whose values will be truncated to
1000 characters.
""",

        "CheckbuttonExcelFixDataRange": """
Enable this option if your Excel sheets have a lot of of empty lines in the end.
""",

    }

    ############################################################################

    @classmethod
    def run(cls, args):
        max_len_custom = None

        if args.length_limit:
            max_len_custom = {}

            for col in args.truncate_1k.split(","):
                col = col.strip()

                if col:
                    max_len_custom[col] = 1000

            for col in args.truncate_4k.split(","):
                col = col.strip()

                if col:
                    max_len_custom[col] = 4000

        convert_excel = ExcelConverter(
            callback=lambda row, _: row,
            sheet_mask=args.sheet.strip(),
            file_mask=args.output.strip(),
            row_start=args.row_start,
            row_stop=args.row_stop,
            last_column=args.last_column,
            max_len_default=args.length_limit,
            max_len_custom=max_len_custom,
            last_cell_limit=1000 if args.fix_data_range else None)

        for file in process_files(args):
            convert_excel(file)

    ############################################################################

    @classmethod
    def _add_arguments(cls, parser):
        parser.add_argument(
            "-s", "--sheet",
            default="*",
            metavar="MASK",
            help="sheet name mask (default: *)",
        )
        parser.add_argument(
            "-o", "--output",
            default="!\\!.csv",
            metavar="MASK",
            help="output file mask (default: !\\!.csv)",
        )
        parser.add_argument(
            "-f", "--row-start",
            type=int,
            default=0,
            metavar="N",
            help="start converting from N row (skip N-1 first rows)",
        )
        parser.add_argument(
            "-t", "--row-stop",
            type=int,
            default=0,
            metavar="N",
            help="stop converting on reaching N row in excel sheet",
        )
        parser.add_argument(
            "-c", "--last-column",
            metavar="COL",
            help="convert data which lays between A and COL",
        )
        parser.add_argument(
            "-i", "--length-limit",
            type=int,
            metavar="N",
            help="truncate value length to N chars",
        )
        parser.add_argument(
            "-u", "--truncate-1k",
            default="",
            metavar="COL1,COL2,...",
            help="truncate values in COL to length 1000 chars",
        )
        parser.add_argument(
            "-w", "--truncate-4k",
            default="",
            metavar="COL1,COL2,...",
            help="truncate values in COL to length 4000 chars",
        )
        parser.add_argument(
            "-j", "--fix-data-range",
            action="store_true",
            help=("stop converting if 1000 equal rows found one after another "
                  "(incorrect data range in Excel 2007+)"),
        )
        cls._add_files_arguments(parser)

    ############################################################################

    @classmethod
    def _validate_cmd_args(cls, var):
        cls._validate_files(var)

        if not var.excel_sheet.strip():
            raise InvalidCommandArgs("Excel sheet mask must be specified!")

        if not var.excel_output.strip():
            raise InvalidCommandArgs("Output file mask must be specified!")

        for var_name, var_desc in (("excel_row_start", "Start row"),
                                   ("excel_row_stop", "Stop row"),
                                   ("excel_length_limit", "Length limit")):
            value = var[var_name].strip()

            if not value:
                continue

            try:
                value = int(value)
                assert value >= 0

            except (ValueError, AssertionError):
                raise InvalidCommandArgs(
                    "{} must be non-negative integer number.".format(var_desc))

        last_column = var.excel_last_column.strip().upper()

        if last_column:
            if not re.match(r"[A-Z]{1,3}|\d+", last_column):
                raise InvalidCommandArgs(
                    "Invalid value of last column! Must be A..XFD or a number.")

        for var_name, var_desc in (("excel_truncate_1k", "Truncate 1k"),
                                   ("excel_truncate_4k", "Truncate 4k")):
            value = var[var_name].strip().strip(",").strip().upper()

            if not value:
                continue

            if not re.match(r"(([A-Z]{1,3}|\d+)\s*,\s*)+", value):
                raise InvalidCommandArgs(
                    ("Invalid value of {}! Must be something like this: "
                     "BA,BB,BX or 12,13,26").format(var_desc))

    ############################################################################

    @classmethod
    def _get_cmd_args(cls, var):
        args = []

        args.extend(["--sheet", var.excel_sheet.strip()])
        args.extend(["--output", var.excel_output.strip()])

        row_start = var.excel_row_start.strip()

        if row_start:
            args.extend(["--row-start", row_start])

        row_stop = var.excel_row_stop.strip()

        if row_stop:
            args.extend(["--row-stop", row_stop])

        last_column = var.excel_last_column.strip().upper()

        if last_column:
            args.extend(["--last-column", last_column])

        length_limit = var.excel_length_limit.strip()

        if length_limit:
            args.extend(["--length-limit", length_limit])

        truncate_1k = var.excel_truncate_1k.strip().strip(",").strip().upper()

        if truncate_1k:
            args.extend(["--truncate-1k", truncate_1k])

        truncate_4k = var.excel_truncate_4k.strip().strip(",").strip().upper()

        if truncate_4k:
            args.extend(["--truncate-4k", truncate_4k])

        if var.excel_fix_data_range:
            args.append("--fix-data-range")

        return args
