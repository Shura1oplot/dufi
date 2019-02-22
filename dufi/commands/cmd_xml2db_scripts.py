# [SublimeLinter @python:3]

import os

from .base import Command
from .xml2db import XML2DB
from .sqlhelpers import get_sql_name
from .arghelpers import GUIOpt


class XML2DBScripts(XML2DB):

    BCP = 'bcp "%DATABASE%.dbo.{}" in "{}" -S "%SERVER%" -T -m 0 -w -k'

    def __init__(self, output_dir=None):
        super(XML2DBScripts, self).__init__()

        self.output_dir = output_dir

    def create_scripts(self, server, database, compressed):
        assert self.output_dir

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self._create_sql_script(
            os.path.join(self.output_dir, "1_init_db.sql"),
            database)
        self._create_bcp_script(
            os.path.join(self.output_dir, "2_upload.bat"),
            server, database, compressed)

    def _create_sql_script(self, file, database):
        fp = open(file, "w")

        fp.write("USE {};\nGO\n\n".format(get_sql_name(database)))

        for elem, children in self.elem_nest.items():
            if "@" in elem:
                continue

            columns = ["    [id] bigint NOT NULL PRIMARY KEY",
                       "    [parent_id] bigint NOT NULL"]

            if self.elem_size[elem]:
                columns.append("    [value] {}".format(
                    self._get_str_type(self.elem_size[elem])))

            for child in children:
                if "@" in child and self.elem_size[child]:
                    columns.append("    {} {}".format(
                        get_sql_name(child),
                        self._get_str_type(self.elem_size[child])))

            fp.write("DROP TABLE IF EXISTS {};\nGO\n\n".format(
                get_sql_name(elem)))
            fp.write("CREATE TABLE {} (\n".format(get_sql_name(elem)))
            fp.write(",\n".join(columns))
            fp.write("\n);\nGO\n\n")

        fp.close()

    @staticmethod
    def _get_str_type(size):
        if size <= 4000:
            return "nvarchar({})".format(size)

        return "varbinary(max)"

    def _create_bcp_script(self, file, server, database, compressed):
        fp = open(file, "w")

        fp.write("@ECHO OFF\n\n")
        fp.write('SET "SERVER={}"\n'.format(
            server.replace('"', '""')))
        fp.write('SET "DATABASE={}"\n'.format(
            get_sql_name(database).replace('"', '""')))

        file_ext = ".txt"

        if compressed:
            file_ext += ".xz"
            fp.write('SET "DECOMPRESS=7z e"\n')

        fp.write("\n")

        for elem, children in self.elem_nest.items():
            if "@" in elem:
                continue

            fname = elem + file_ext

            if compressed:
                fp.write('%DECOMPRESS% "{}"\n'.format(fname.replace('"', '""')))
                fname, ext = fname.rsplit(".", 1)
                assert ext.lower() in {"gz", "bz2", "lzma", "xz"}

            fp.write(self.BCP.format(
                get_sql_name(elem), fname.replace('"', '""')))

            if compressed:
                fp.write('\nDEL /F /Q "{}"\n'.format(fname.replace('"', '""')))

            fp.write("\n")

        fp.write("\nPAUSE\n")

        fp.close()


class XML2DBScriptsCommand(Command):

    cli_command = "xml2db-scripts"
    cli_command_aliases = ()
    cli_command_help = ("create SQL and bcp scripts for uploading XML files "
                        "into MS SQL Server database")
    cli_files_required = False

    ############################################################################

    @classmethod
    def run(cls, args):
        xml2db = XML2DBScripts(output_dir=args.output_dir)
        xml2db.load_schema(args.schema)
        xml2db.create_scripts(args.server, args.database, args.compressed)

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
            "-s", "--server",
            metavar="ADDR",
            default="ru-mowras002",
            help="MS SQL Server address")

        parser.add_argument(
            "-d", "--database",
            metavar="DB",
            default="my_database",
            help="MS SQL Server database name")

        parser.add_argument(
            "-c", "--compressed",
            action="store_true",
            help="flat files are compressed")

        parser.add_argument(
            "-o", "--output-dir",
            metavar="DIR",
            required=True,
            help="directory to save scripts",
            **guiopt(action="browse_dir",
                     box_args={"mustexist": False}))
