# [SublimeLinter @python:3]

from .xml2db import XML2DBConvert

from .base import Command
from .arghelpers import GUIOpt, process_files
from ..utils import echo


class XML2DBCommand(Command):

    cli_command = "xml2db-convert"
    cli_command_aliases = ()
    cli_command_help = "convert XML files into flat text files"

    ############################################################################

    @classmethod
    def run(cls, args):
        xml2db = XML2DBConvert(out_mode=args.out_mode,
                               output_dir=args.output_dir,
                               cmd_line=args.cmd_line)
        xml2db.load_schema(args.schema)

        if args.stdin:
            xml2db.feed(None)

        else:
            for file in process_files(args):
                echo("Progress: 0%")
                xml2db.feed(file)
                echo("Progress: 100%")

        xml2db.finalize()

    ############################################################################

    @classmethod
    def _add_arguments(cls, parser):
        guiopt = GUIOpt(parser)

        parser.add_argument(
            "-t", "--schema",
            metavar="FILE",
            required=True,
            help="schema file",
            **guiopt(action="browse_file",
                     box_args={"filetypes": [["JSON", "*.json"], ]}))

        parser.add_argument(
            "-m", "--out-mode",
            choices=("plain", "compress", "process"),
            default="plain",
            help=("output mode: "
                  "`plain` - save plain flat files, "
                  "`compress` - save compressed flat files, "
                  "`process` - send flat files to other program"))

        parser.add_argument(
            "-o", "--output-dir",
            metavar="DIR",
            help="directory to save flat files",
            **guiopt(action="browse_dir",
                     box_args={"mustexist": False}))

        parser.add_argument(
            "-C", "--cmd-line",
            metavar="CMD",
            help="command line for out mode `process`")

        parser.add_argument(
            "-i", "--stdin",
            action="store_true",
            help="read XML content from stdin")

        cls._add_files_arguments(parser)
