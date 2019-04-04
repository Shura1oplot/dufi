# [SublimeLinter @python:3]

import os
import codecs
import re
from pathlib import Path

from .iconv import iconv

from .base import Command, InvalidCommandArgs
from .arghelpers import GUIOpt, format_file_path, get_separator, process_files
from ..utils import echo


class ConvertCommand(Command):

    cli_command = "convert"
    cli_command_aliases = ()
    cli_command_help = "convert an encoding and a format of the files (batch mode)"

    gui_order = 5
    gui_command = "Convert & Merge"
    gui_description = "Convert an encoding and a format (CSV -> TSV) of the files"
    gui_files_info_label_id = "LabelConvertFilesInfo"
    gui_info_message_widget = "MessageConvertInfo"

    gui_variables = ("convert_output", "convert_from_code", "convert_to_code", "convert_format",
                     "separator", "with_qualifier",
                     "convert_add_filename", "convert_drop_first_row",
                     "convert_drop_first_row_except_first_file")
    gui_default = {"convert_from_code": "UTF-8",
                   "convert_to_code": "CP1251 (Windows)"}
    gui_switches = {
        ("ComboboxConvertSeparator",
         "CheckbuttonConvertWithQuotes",
         "CheckbuttonConvertAddFilenames",
         "CheckbuttonConvertDropFirstRow"): "convert_format",

        "CheckbuttonConvertDropFirstRowExceptFirstFile":
            (all, "convert_format", "convert_drop_first_row"),
    }

    gui_help_tooltips = {

        "LabelConvertOutputHelp": """
Buttons:
 D... - select output directory
 F... - select output file

Mask rules:
 Each ! will be replaced by a part of the full file path:
 1st ! - directory, 2nd ! - name w/o extension, 3rd ! - file extension
 For example, we are going to process: 'C:\\JET\\journal_entries.csv'.
 With mask '!\\!_NEW.!' output file will be 'C:\\JET\\journal_entries_NEW.csv'.
 With mask '!\\NEW\\!.!' output file will be 'C:\\JET\\NEW\\journal_entries.csv.
""",

        "CheckbuttonConvertDouledQuotes": """
Format conversion constraints:
Quotation marks inside text fields must be doubled.
"""

    }

    ############################################################################

    @classmethod
    def run(cls, args):
        for i, file in enumerate(process_files(args)):
            file = os.path.abspath(file)
            file_out = os.path.abspath(format_file_path(args.output, file))

            if Path(file) == Path(file_out):
                echo("ERROR: input and output files must be different")
                return 1

            os.makedirs(os.path.dirname(file_out), exist_ok=True)

            if not i:
                with open(file_out, "w"):
                    pass

            if args.convert_format:
                separator = get_separator(args)
            else:
                separator = None

            drop_first_row = args.drop_first_row

            if args.except_first_file:
                if args.drop_first_row:
                    if not i:
                        drop_first_row = False

            iconv(from_code=args.from_code,
                  to_code=args.to_code,
                  inputfile=file,
                  output=file_out,
                  separator=separator,
                  with_qualifier=args.with_qualifier,
                  add_filename=args.add_filename,
                  drop_first_row=drop_first_row)

        return 0

    ############################################################################

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_coding_arguments(parser)
        cls._add_csv_arguments(parser)
        guiopt = GUIOpt(parser)

        parser.add_argument(
            "-c", "--convert-format",
            action="store_true",
            help="convert format of files from CSV to TSV"
        )
        parser.add_argument(
            "-n", "--add-filename",
            action="store_true",
            help="add filename as the first column"
        )
        parser.add_argument(
            "-d", "--drop-first-row",
            action="store_true",
            help="drop first row of each file"
        )
        parser.add_argument(
            "-D", "--except-first-file",
            action="store_true",
            help="exclude first file from dropping header row"
        )
        parser.add_argument(
            "-o", "--output",
            default="!\\!_NEW.!",
            metavar="FILE_MASK",
            help="specify output files mask (default: !\\!_NEW.!)",
            **guiopt(action="browse_file")
        )

        cls._add_files_arguments(parser)

    ############################################################################

    @classmethod
    def _validate_cmd_args(cls, var):
        cls._validate_files(var)

        for code in (var.convert_from_code, var.convert_to_code):
            code = code.strip()

            if not code:
                raise InvalidCommandArgs(
                    "Both source and output encodings must be specified!")

            m = re.match(r"^([^()]+)( \(.*\))?$", code)

            if not m:
                raise InvalidCommandArgs("Invalid encoding: {!r}".format(code))

            enc = m.group(1).strip().lower().replace("_", "-").replace(" ", "-")

            if not re.match(r"^utf-(8|(16|32)(le|be))-sig$", enc):
                try:
                    codecs.lookup(enc)
                except LookupError:
                    raise InvalidCommandArgs("Invalid encoding: {!r}".format(enc))

    ############################################################################

    @classmethod
    def _get_cmd_args(cls, var):
        args = []

        args.extend(["--from-code", cls._extract_encoding(var.convert_from_code.strip())])
        args.extend(["--to-code", cls._extract_encoding(var.convert_to_code.strip())])
        args.extend(["--output", var.convert_output.strip()])

        if var.convert_format:
            args.append("--convert-format")

            args.extend(cls._get_cmd_args_separator(var))

            if var.with_quotes:
                args.append("--with-qualifier")

            if var.convert_add_filename:
                args.append("--add-filename")

            if var.convert_drop_first_row:
                args.append("--drop-first-row")

                if var.convert_drop_first_row_except_first_file:
                    args.append("--except-first-file")

        return args

    @staticmethod
    def _extract_encoding(s):
        m = re.match(r"^([^()]+)( \(.*\))?$", s)
        return m.group(1).strip().lower().replace("_", "-").replace(" ", "-")
