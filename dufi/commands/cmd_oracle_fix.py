# [SublimeLinter @python:3]

import os

from .base import Command
from .arghelpers import process_files
from ..utils import echo


class OracleFixCommand(Command):

    cli_command = "oracle-fix"
    cli_command_aliases = ("oracle", )
    cli_command_help = "repair files with an EOL placed each N characters"

    gui_order = 4
    gui_command = "Fix Oracle Extraction"
    gui_description = "Repair files with an EOL placed each 80 or 100 characters"
    gui_files_info_label_id = "LabelOracleFilesInfo"
    gui_info_message_widget = "MessageOracleInfo"

    ############################################################################

    @classmethod
    def run(cls, args):
        for file in process_files(args):
            fname_base, fname_ext = os.path.splitext(file)

            if fname_base.upper().endswith("_FIXED"):
                echo("WARNING: file already fixed, skipped")
                continue

            fname_fixed = "{}_FIXED{}".format(fname_base, fname_ext)
            file_size = os.path.getsize(file)

            progress = None

            with open(file, "rb") as fpi, open(fname_fixed, "wb") as fpo:
                fpi_tell = fpi.tell

                for line in fpi:
                    fpo.write(line.rstrip(b"\r\n") or b"\r\n")

                    new_progess = 100 * fpi_tell() // file_size

                    if new_progess != progress:
                        echo("Progress: {}%".format(new_progess))
                        progress = new_progess

        if progress != 100:
            echo("Progress: 100%")

    ############################################################################

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_files_arguments(parser)

    ############################################################################

    @classmethod
    def _validate_cmd_args(cls, var):
        cls._validate_files(var)

    ############################################################################

    @classmethod
    def _get_cmd_args(cls, var):
        return []
