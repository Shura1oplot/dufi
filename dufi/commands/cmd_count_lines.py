# [SublimeLinter @python:3]

from .base import Command
from .arghelpers import get_files
from ..utils import echo


class CountLinesCommand(Command):

    cli_command = "count-lines"
    cli_command_aliases = ("cl", "wcl")
    cli_command_help = "count lines in files"

    gui_order = 7
    gui_command = "Count Lines"
    gui_description = "Count lines in files."
    gui_files_info_label_id = "LabelCountLinesFilesInfo"
    gui_info_message_widget = "MessageCountLinesFiles"

    ############################################################################

    @classmethod
    def run(cls, args):
        for fname in get_files(args):
            count = 0

            for _ in open(fname, "rb"):
                count += 1

            echo("{}: {}".format(fname, count))

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
