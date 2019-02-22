# [SublimeLinter @python:3]

from .base import Command
from .arghelpers import GUIOpt, process_files


class ConcatCommand(Command):

    cli_command = "concat"
    cli_command_aliases = ()
    cli_command_help = "concatenate text files"

    ############################################################################

    @classmethod
    def run(cls, args):
        with open(args.output_file, "wb") as fpo:
            for file in process_files(args):
                with open(file, "rb") as fpi:
                    while True:
                        data = fpi.read(1000)

                        if not data:
                            break

                        fpo.write(data)

    ############################################################################

    @classmethod
    def _add_arguments(cls, parser):
        guiopt = GUIOpt(parser)

        parser.add_argument(
            "-o", "--output-file",
            required=True,
            metavar="FILE",
            help="output file name",
            **guiopt(action="browse_file",
                     box_type="save",
                     box_args={"filetypes": [["All types", "*.*"], ],
                               "defaultextension": ".txt",
                               "initialfile": "output.txt"})
        )
        cls._add_files_arguments(parser)

    ############################################################################

    @classmethod
    def _validate_cmd_args(cls, var):
        cls._validate_files(var)
