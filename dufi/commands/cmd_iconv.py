# [SublimeLinter @python:3]

from .base import Command
from .iconv import iconv
from .arghelpers import GUIOpt, type_single_byte, get_separator


class IconvCommand(Command):

    cli_command = "iconv"
    cli_command_aliases = ()
    cli_command_help = "convert file encoding and format (CSV -> TSV)"
    cli_files_required = False

    ############################################################################

    @classmethod
    def run(cls, args):
        return iconv(args.from_code, args.to_code, args.inputfile, args.output,
                     get_separator(args) if args.convert_format else None)

    ############################################################################

    @classmethod
    def _add_arguments(cls, parser):
        guiopt = GUIOpt(parser)

        cls._add_coding_arguments(parser)
        parser.add_argument(
            "-o", "--output",
            metavar="FILE",
            help="specify output file (instead of stdout)",
            **guiopt(action="browse_file")
        )
        parser.add_argument(
            "-c", "--convert-format",
            action="store_true",
            help="convert format of files from CSV with qualifier to TSV"
        )
        parser.add_argument(
            "-s", "--separator",
            type=type_single_byte,
            default=",",
            help="character that separates fields in a row (default: ',')",
        )
        parser.add_argument(
            "inputfile",
            nargs="?",
            **guiopt(action="browse_file")
        )
