# [SublimeLinter @python:3]

import os

from .base import Command
from .arghelpers import process_files
from .cdufi import cr_to_space


class CRToSpaceCommand(Command):

    cli_command = "fix-eol"
    cli_command_aliases = ("cr-to-space", )
    cli_command_help = "replace CR character by Space"

    gui_order = 6
    gui_command = "Fix EOL"
    gui_description = "Convert in place CR+LF lines ending style to LF only."
    gui_files_info_label_id = "LabelCRToSpaceFilesInfo"
    gui_info_message_widget = "MessageCRToSpaceInfo"

    ############################################################################

    @classmethod
    def run(cls, args):
        for file in process_files(args):
            with open(file, "r+b") as fp:
                cr_to_space(fp, os.path.getsize(file))

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
