# [SublimeLinter @python:3]

import os
import re

from .base import Command, InvalidCommandArgs
from .arghelpers import process_files, format_file_path
from ..utils import echo


class JoinRowsCommand(Command):

    cli_command = "csv-join-rows"
    cli_command_aliases = ("join-rows", "jr")
    cli_command_help = "merge rows which (not) start with a specified (regex) pattern"

    gui_order = 8
    gui_command = "CSV Join Rows"
    gui_description = "Merge rows which (not) start with a specified (regex) pattern"
    gui_files_info_label_id = "LabelJoinRowsFilesInfo"
    gui_info_message_widget = "MessageJoinRowsParameters"

    gui_variables = ("join_rows_pattern", "join_rows_regex", "join_rows_negative")

    ############################################################################

    @classmethod
    def run(cls, args):
        pattern = args.pattern

        if isinstance(pattern, str):
            pattern = pattern.encode("cp1251")

        if args.regex:
            join_rows = cls._join_rows_regex
        else:
            join_rows = cls._join_rows_plain

        for file in process_files(args):
            file_out = format_file_path("!\\!_NEW.!", file)
            file_size = os.path.getsize(file)

            with open(file, "rb") as fpi, open(file_out, "wb") as fpo:
                join_rows(fpi, fpo, pattern, args.negative, file_size)

    @staticmethod
    def _join_rows_plain(fpi, fpo, pattern, negative, file_size):
        fpo_write = fpo.write
        fpi_tell = fpi.tell

        fpi_it = iter(fpi)
        fpo_write(next(fpi_it).rstrip(b"\r\n"))

        progress = None

        for line in fpi_it:
            match = line.startswith(pattern)

            if negative:
                match = not match

            if match:
                fpo_write(line[len(pattern):].rstrip(b"\r\n"))
            else:
                fpo_write(b"\r\n")
                fpo_write(line.rstrip(b"\r\n"))

            new_progess = 100 * fpi_tell() // file_size

            if new_progess != progress:
                echo("Progress: {}%".format(new_progess))
                progress = new_progess

        fpo_write(b"\r\n")

        if progress != 100:
            echo("Progress: 100%")

    @staticmethod
    def _join_rows_regex(fpi, fpo, pattern, negative, file_size):
        fpo_write = fpo.write
        fpi_tell = fpi.tell

        re_match = re.compile(b"^" + pattern).match

        fpi_it = iter(fpi)
        fpo_write(next(fpi_it).rstrip(b"\r\n"))

        progress = None

        for line in fpi_it:
            match = re_match(line)

            if negative:
                match = not match

            if not match:
                fpo_write(b"\r\n")

            fpo_write(line.rstrip(b"\r\n"))

            new_progess = 100 * fpi_tell() // file_size

            if new_progess != progress:
                echo("Progress: {}%".format(new_progess))
                progress = new_progess

        fpo_write(b"\r\n")

        if progress != 100:
            echo("Progress: 100%")

    ############################################################################

    @classmethod
    def _add_arguments(cls, parser):
        parser.add_argument(
            "-p", "--pattern",
            required=True,
            help="pattern to match the beginning of each row",
        )
        parser.add_argument(
            "-r", "--regex",
            action="store_true",
            help=("pattern is regex ('^' will be added at the beginning of the "
                  "pattern)"),
        )
        parser.add_argument(
            "-n", "--negative",
            action="store_true",
            help="concat lines which do not match the pattern",
        )
        cls._add_files_arguments(parser)

    ############################################################################

    @classmethod
    def _validate_cmd_args(cls, var):
        cls._validate_files(var)

        if not var.join_rows_pattern.strip():
            raise InvalidCommandArgs("Pattern string must by specified!")

    ############################################################################

    @classmethod
    def _get_cmd_args(cls, var):
        args = []
        args.extend(["--pattern", var.join_rows_pattern.strip()])

        if var.join_rows_regex:
            args.append("--regex")

        if var.join_rows_negative:
            args.append("--negative")

        return args
