# [SublimeLinter @python:3]

import os
import codecs
from pathlib import Path
import re
import csv

from .base import Command, InvalidCommandArgs
from .arghelpers import GUIOpt, get_separator, get_files, process_files
from ..utils import echo


class MergeCSVCommand(Command):

    cli_command = "merge-csv"
    cli_command_aliases = ()
    cli_command_help = "merge a number of CSV files into one using column names"

    # gui_order = 5
    # gui_command = "Merge CSV"
    # gui_description = "Merge a number of CSV files into one using column names"
    # gui_files_info_label_id = "LabelMergeCSVFilesInfo"
    # gui_info_message_widget = "MessageMergeCSVInfo"

    # gui_variables = ("merge_csv_output",
    #                  "merge_csv_encoding",
    #                  "separator", "with_qualifier")
    # gui_default = {"merge_csv_encoding": "CP1251 (Windows)"}
    # gui_switches = {
    #     ("ComboboxConvertSeparator",
    #      "CheckbuttonConvertWithQuotes",
    #      "CheckbuttonConvertAddFilenames",
    #      "CheckbuttonConvertDropFirstRow"): "convert_format",

    #     "CheckbuttonConvertDropFirstRowExceptFirstFile":
    #         (all, "convert_format", "convert_drop_first_row"),
    # }

#     gui_help_tooltips = {

#         "LabelConvertOutputHelp": """
# Buttons:
#  D... - select output directory
#  F... - select output file

# Mask rules:
#  Each ! will be replaced by a part of the full file path:
#  1st ! - directory, 2nd ! - name w/o extension, 3rd ! - file extension
#  For example, we are going to process: 'C:\\JET\\journal_entries.csv'.
#  With mask '!\\!_NEW.!' output file will be 'C:\\JET\\journal_entries_NEW.csv'.
#  With mask '!\\NEW\\!.!' output file will be 'C:\\JET\\NEW\\journal_entries.csv.
# """,

#         "CheckbuttonConvertDouledQuotes": """
# Format conversion constraints:
# Quotation marks inside text fields must be doubled.
# """

#     }

    ############################################################################

    @classmethod
    def run(cls, args):
        file_out = Path(args.output)

        csv_kargs = {
            "delimiter": chr(get_separator(args)),
            "quotechar": '"' if args.with_qualifier else None,
        }

        field_names = []

        for file in get_files(args):
            file = Path(file)

            if file == file_out:
                echo("ERROR: input and output files must be different")
                return 1

            with open(file, "r", encoding=args.encoding, newline="") as fpi:
                try:
                    header_row = next(iter(csv.reader(fpi, **csv_kargs)))
                except StopIteration:
                    echo("WARNING: empty CSV file: {}".format(file))
                    continue

            for name in cls._get_header(header_row):
                if name not in field_names:
                    field_names.append(name)

        if not field_names:
            echo("ERROR: cannot collect field names")
            return 1

        os.makedirs(file_out.parent, exist_ok=True)

        with open(file_out, "w", encoding=args.encoding, newline="") as fpo:
            csv_writer = csv.writer(fpo, **csv_kargs)

            csv_writerow = csv_writer.writerow
            csv_writerow(field_names)

            for file in process_files(args):
                file_size = os.path.getsize(file)
                progress = None

                with open(file, "r", encoding=args.encoding, newline="") as fpi:
                    fpi_tell = fpi.buffer.tell

                    csv_reader = csv.reader(fpi, **csv_kargs)
                    csv_reader_iter = iter(csv_reader)

                    try:
                        header = cls._get_header(next(csv_reader_iter))
                    except StopIteration:
                        continue

                    for row in csv_reader_iter:
                        d = dict(zip(header, row))
                        csv_writerow([d.get(name, "") for name in field_names])

                        new_progess = 100 * fpi_tell() // file_size

                        if new_progess != progress:
                            echo("Progress: {}%".format(new_progess))
                            progress = new_progess

                if progress != 100:
                    echo("Progress: 100%")

        return 0

    @classmethod
    def _get_header(cls, row):
        header = []
        name_counter = {}

        for name in row:
            if not name:
                name = "empty"

            if name in name_counter:
                new_name = "{}_{}".format(name, name_counter[name])
                name_counter[name] += 1
                name = new_name

            else:
                name_counter[name] = 1

            header.append(name)

        return header

    ############################################################################

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_csv_arguments(parser)
        guiopt = GUIOpt(parser)

        parser.add_argument(
            "-e", "--encoding",
            default="cp1251",
            metavar="ENCODING",
            help="encoding of the CSV files (default: cp1251)"
        )
        parser.add_argument(
            "-o", "--output",
            required=True,
            metavar="FILE",
            help="specify output file",
            **guiopt(action="browse_file",
                     box_type="save",
                     box_args={"filetypes": [["CSV file", "*.csv"],
                                             ["Text file", "*.txt"],
                                             ["All types", "*.*"]],
                               "defaultextension": ".csv",
                               "initialfile": "output.csv"})
        )

        cls._add_files_arguments(parser)

    ############################################################################

    @classmethod
    def _validate_cmd_args(cls, var):
        cls._validate_files(var)

        code = var.merge_csv_encoding.strip()

        if not code:
            raise InvalidCommandArgs("Encodings not specified!")

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

        args.extend(["--encoding", cls._extract_encoding(
            var.merge_csv_encoding.strip())])

        args.extend(["--output", var.merge_csv_output.strip()])

        args.extend(cls._get_cmd_args_separator(var))

        if var.with_quotes:
            args.append("--with-qualifier")

        return args

    @staticmethod
    def _extract_encoding(s):
        m = re.match(r"^([^()]+)( \(.*\))?$", s)
        return m.group(1).strip().lower().replace("_", "-").replace(" ", "-")
