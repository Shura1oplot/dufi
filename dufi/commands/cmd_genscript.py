# [SublimeLinter @python:3]

import os
from itertools import zip_longest
import re
import win32console

from .base import Command, InvalidCommandArgs
from .sqlhelpers import sqlfmt, get_sql_name
from .arghelpers import get_separator, get_files, process_files
from ..utils import echo


class GenerateScriptCommand(Command):

    cli_command = "create-script"
    cli_command_aliases = ("create-upload-script", "crupsc", )
    cli_command_help = "create SQL script and bcp batch for data uploading"

    gui_order = 9
    gui_command = "Create Stript"
    gui_description = "Create 'CREATE TABLE' SQL script and data uploading BAT script."
    gui_files_info_label_id = "LabelScriptFilesInfo"
    gui_info_message_widget = "MessageScriptInfo"

    gui_variables = ("separator", "script_regex_fname", "script_regex_table",
                     "script_header", "script_fast")
    gui_default = {"script_header": 1}

    gui_help_tooltips = {
        "CheckbuttonScriptWithQuotes": "Not supported by BULK INSERT.",
    }

    ############################################################################

    @classmethod
    def run(cls, args):
        files = get_files(args)
        regex_fname = args.regex_fname
        regex_table = args.regex_table

        sep = bytes([get_separator(args)])
        headers = {}
        lengths = {}

        for file in files:
            file_name = os.path.basename(file)
            table_name = re.sub(regex_fname, regex_table, os.path.basename(file))

            if not table_name:
                raise ValueError("Cannot determine table name: {}".format(file_name))

        base_dir = os.path.dirname(files[0])

        def round_length(x):
            if x > 1000:
                return 4000
            if x > 255:
                return 1000
            if x > 50:
                return 255
            return 50

        for file in process_files(args):
            file_size = os.path.getsize(file)
            progress = None

            with open(file, "rb") as fpi:
                fpi_tell = fpi.tell

                it = iter(fpi)
                lns = []

                if args.has_header:
                    header = [x.decode("cp1251") for x in next(it).rstrip(b"\r\n").split(sep)]
                    lns = [1] * len(header)
                else:
                    header = None

                if args.fast_scan:
                    it = (x for i, x in enumerate(it) if i < 1000)

                for i, line in enumerate(it):
                    new_lns = []

                    for x, s in zip_longest(lns, line.rstrip(b"\r\n").split(sep)):
                        if x is None:
                            x = 1

                        if s is None:
                            s = ""

                        new_lns.append(max(x, len(s)))

                    lns = new_lns

                    new_progess = 100 * fpi_tell() // file_size

                    if new_progess != progress:
                        echo("Progress: {}%".format(new_progess))
                        progress = new_progess

                if args.fast_scan:
                    lns = [round_length(x) for x in lns]

                headers[file] = header
                lengths[file] = lns

            if progress != 100:
                echo("Progress: 100%")

        query = []
        batch = ['set "SERVER=localhost"',
                 'set "DATABASE=my_database"']

        for file, header in headers.items():
            file_name = os.path.basename(file)
            table_name = re.sub(regex_fname, regex_table, os.path.basename(file))

            if not table_name:
                raise ValueError("Cannot determine table name: {}".format(file_name))

            bcp_cmd = ('bcp "[%DATABASE%].dbo.{}" in "{}" -S "%SERVER%" '
                       '-T -m 0 -c -C 1251 -k').format(
                get_sql_name(table_name), file.replace('"', '""'))

            if sep != b"\t":
                bcp_cmd += ' -t "{}"'.format(sep.decode("ascii").replace('"', '""'))

            if args.has_header:
                bcp_cmd += " -F 2"

            batch.append(bcp_cmd)

            lns = lengths[file]

            if header is None:
                header = ["Column {}".format(i + 1) for i in range(len(lns))]

            sql = ["IF OBJECT_ID({table.name.str}) IS NOT NULL",
                   "    DROP TABLE {table.name};",
                   "GO", "",
                   "CREATE TABLE {table.name} ("]

            for i, (col_name, col_len) in enumerate(zip(header, lns)):
                sql.append(sqlfmt("   " + ("," if i else " ") \
                    + "{.name} nvarchar({.int})", col_name, col_len))

            sql.append(");")
            sql.append("GO")
            sql.append("")

            query.append(sqlfmt("\n".join(sql), table=table_name))

        query_file = os.path.join(base_dir, "dufi_create_tables.sql")

        with open(query_file, "w") as fp:
            fp.write("\n".join(query))

        batch_file = os.path.join(base_dir, "dufi_upload.bat")

        cp = win32console.GetConsoleOutputCP()

        with open(batch_file, "w", encoding="cp{}".format(cp)) as fp:
            fp.write("\n".join(batch))

        echo("Files `{}` and `{}` save into `{}`".format(
            os.path.basename(query_file),
            os.path.basename(batch_file),
            base_dir))

    ############################################################################

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_csv_arguments(parser, qualifier=False)
        parser.add_argument(
            "-a", "--regex-fname",
            default=r"(.*)\.csv",
            metavar="MASK",
            help="regex mask for file name parsing (default: '(.*)\\.csv')",
        )
        parser.add_argument(
            "-b", "--regex-table",
            default=r"\1",
            metavar="MASK",
            help="mask to format table name (default: '\\1')",
        )
        parser.add_argument(
            "-e", "--has-header",
            action="store_true",
            help="dump files has headers",
        )
        parser.add_argument(
            "-f", "--fast-scan",
            action="store_true",
            help=("scan first 1000 rows only (all lengths will be aligned with "
                  "50,255,1000,4000 borders)"),
        )
        cls._add_files_arguments(parser)

    ############################################################################

    @classmethod
    def _validate_cmd_args(cls, var):
        cls._validate_files(var)
        cls._validate_separator(var)

        if not var.script_regex_fname.strip() and not var.script_regex_table.strip():
            raise InvalidCommandArgs("Regex masks must be specified!")

    ############################################################################

    @classmethod
    def _get_cmd_args(cls, var):
        args = []
        args.extend(cls._get_cmd_args_separator(var))

        script_regex_fname = var.script_regex_fname.strip()

        if script_regex_fname:
            args.extend(["--regex-fname", script_regex_fname])

        script_regex_table = var.script_regex_table.strip()

        if script_regex_table:
            args.extend(["--regex-table", script_regex_table])

        if var.script_header:
            args.append("--has-header")

        if var.script_fast:
            args.append("--fast-scan")

        return args
