# [SublimeLinter @python:3]

import os

from .base import Command
from .cdufi import concat_lines, repair_csv
from .patch import patch
from .arghelpers import process_files, get_separator


class RepairCommand(Command):

    cli_command = "csv-repair"
    cli_command_aliases = ("repair", )
    cli_command_help = "detect and repair defected lines in csv file"

    gui_order = 2
    gui_command = "CSV Repair"
    gui_description = "Repair incorrect structure of CSV files."
    gui_files_info_label_id = "LabelRepairFilesInfo"
    gui_info_message_widget = "MessageRepairInfo"

    gui_variables = ("separator", "with_quotes", "doubled_qoutes", "remove_embedded_newlines")
    gui_switches = {
        "CheckbuttonDouledQuotes": "with_quotes",
        "CheckbuttonRemoveEmdebbedNewlines": (all, "with_quotes", "doubled_qoutes")
    }

    ############################################################################

    @classmethod
    def run(cls, args):
        for file in process_files(args):
            cls._repair_csv(file, args)

    @staticmethod
    def _repair_csv(file, args):
        patch_file = file + ".patch"
        file_size = os.path.getsize(file)

        if not args.with_qualifier:
            with open(file, "rb") as fpi, open(patch_file, "w") as fpo:
                concat_lines(fpi, fpo, file_size, get_separator(args), -1)

            patch(file, patch_file)
            return

        with open(file, "rb") as fpi, open(patch_file, "w") as fpo:
            count = repair_csv(
                fpi, fpo, file_size, get_separator(args), b'"'[0], b"'"[0],
                args.doubled_qualifier, args.remove_embedded_newlines)

        if count > 0:
            patch(file, patch_file)

    ############################################################################

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_csv_arguments(parser)
        parser.add_argument(
            "-b", "--doubled-qualifier",
            action="store_true",
            help=("double quotes in values are doubled in the csv file "
                  "(--with-qualifier must be set)"),
        )
        parser.add_argument(
            "-e", "--remove-embedded-newlines",
            action="store_true",
            help="remove newlines embedded into fields (--with-qualifier must be set)",
        )
        cls._add_files_arguments(parser)

    ############################################################################

    @classmethod
    def _validate_cmd_args(cls, var):
        cls._validate_files(var)
        cls._validate_separator(var)

    ############################################################################

    @classmethod
    def _get_cmd_args(cls, var):
        args = []
        args.extend(cls._get_cmd_args_separator(var))

        if var.with_quotes:
            args.append("--with-qualifier")

            if var.doubled_qoutes:
                args.append("--doubled-qualifier")

                if var.remove_embedded_newlines:
                    args.append("--remove-embedded-newlines")

        return args
