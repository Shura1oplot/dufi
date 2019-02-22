# [SublimeLinter @python:3]

from .base import Command
from .arghelpers import process_files, format_file_path


class SampleCommand(Command):

    cli_command = "sample"
    cli_command_aliases = ()
    cli_command_help = "get first 1M of file"

    ############################################################################

    @classmethod
    def run(cls, args):
        for file in process_files(args):
            file_out = format_file_path("!\\!_SAMPLE.!", file)

            with open(file, "rb") as fpi, open(file_out, "wb") as fpo:
                fpo.write(fpi.read(1024 ** 2))

    ############################################################################

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_files_arguments(parser)
