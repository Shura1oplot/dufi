# [SublimeLinter @python:3]

import os

from .base import Command, InvalidCommandArgs
from .cdufi import merge_columns
from .patch import patch
from .arghelpers import type_single_byte, get_separator, process_files


class MergeColumnCommand(Command):

    cli_command = "csv-merge-column"
    cli_command_aliases = ("merge-column", "mc")
    cli_command_help = "remove field separator from values in one column"

    gui_order = 3
    gui_command = "CSV Merge Column"
    gui_description = "Merge text value spreaded into several columns."
    gui_files_info_label_id = "LabelMergeColumnFilesInfo"
    gui_info_message_widget = "MessageMergeColumnInfo"

    gui_variables = ("separator", "merge_column_number", "merge_replacement")

    gui_help_tooltips = {

        "CheckbuttonMergeColumnWithQuotes": """
Files with proper double quotes are not the object
for this command. Use Repair instead.
"""

    }

    ############################################################################

    @classmethod
    def run(cls, args):
        for file in process_files(args):
            patch_file = file + ".patch"

            with open(file, "rb") as fpi, open(patch_file, "w") as fpo:
                merge_columns(
                    fpi, fpo, os.path.getsize(file), get_separator(args),
                    args.column, args.replacement, -1)

            patch(file, patch_file)

    ############################################################################

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_csv_arguments(parser, qualifier=False)
        parser.add_argument(
            "-c", "--column",
            type=int,
            required=True,
            metavar="N",
            help="number of column to join",
        )
        parser.add_argument(
            "-r", "--replacement",
            type=type_single_byte,
            default=b"#"[0],
            metavar="CHAR",
            help="separator replacement (default: #)",
        )
        cls._add_files_arguments(parser)

    ############################################################################

    @classmethod
    def _validate_cmd_args(cls, var):
        cls._validate_files(var)
        cls._validate_separator(var)

        colnum = var.merge_column_number.strip()

        if not colnum:
            raise InvalidCommandArgs("Column number must be specified!")

        try:
            colnum = int(colnum)
        except ValueError:
            raise InvalidCommandArgs(
                "Invalid column number! It must be integer number greater than 0.")

        if colnum <= 0:
            raise InvalidCommandArgs("Column number must be 1 or greater!")

    ############################################################################

    @classmethod
    def _get_cmd_args(cls, var):
        args = []
        args.extend(cls._get_cmd_args_separator(var))
        args.extend(["--column", var.merge_column_number.strip()])
        args.extend(["--replacement", var.merge_replacement.strip()[0]])
        return args
