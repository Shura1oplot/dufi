# [SublimeLinter @python:3]

from .xml2db import XML2DBSchema

from .base import Command
from .arghelpers import GUIOpt, process_files
from ..utils import echo


class XML2DBSchemaCommand(Command):

    cli_command = "xml2db-schema"
    cli_command_aliases = ()
    cli_command_help = "create schema for XML files"

    ############################################################################

    @classmethod
    def run(cls, args):
        ignore_attrs = set()

        if args.ignore_attrs:
            for line in open(args.ignore_attrs, encoding="utf-8"):
                line = line.strip()

                if not line:
                    continue

                ignore_attrs.add(line)

        xml2db = XML2DBSchema(ignore_attrs)

        for file in process_files(args):
            echo("Progress: 0%")
            xml2db.collect_stats(file)
            echo("Progress: 100%")

        xml2db.dump_schema(args.out_schema)

    ############################################################################

    @classmethod
    def _add_arguments(cls, parser):
        guiopt = GUIOpt(parser)

        parser.add_argument(
            "-i", "--ignore-attrs",
            metavar="FILE",
            help="file with list of XML attributes to ignore",
            **guiopt(action="browse_file"))

        parser.add_argument(
            "-t", "--out-schema",
            metavar="FILE",
            required=True,
            help="output schema file",
            **guiopt(action="browse_file",
                     box_type="save",
                     box_args={"filetypes": [["JSON", "*.json"], ],
                               "defaultextension": ".json",
                               "initialfile": "schema.json"}))

        cls._add_files_arguments(parser)
