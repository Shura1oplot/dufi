# [SublimeLinter @python:3]

import os

from .encoding import detect_encoding
from ..base import Command
from ..arghelpers import get_separator, process_files
from ..cdufi import count_seps_with_quotes, count_seps_no_quoting
from ...utils import echo


class DiagnosticsError(Exception):
    pass


class DiagnosticsCommand(Command):

    cli_command = "csv-check"
    cli_command_aliases = ("diagnostics", "diag", "dg")
    cli_command_help = ("validate structure of csv files and save numbers "
                        "of corrupted rows")

    gui_order = 1
    gui_command = "CSV Check"
    gui_description = "Validate structure of CSV files"
    gui_files_info_label_id = "LabelDiagnosticsFilesInfo"
    gui_info_message_widget = "MessageDiagnosticsInfo"

    gui_variables = ("separator", "with_quotes", "execute_compat_tests", "cyrillic")
    gui_default = {"execute_compat_tests": 1,
                   "cyrillic": 1}
    gui_switches = {
        "CheckbuttonCyrillic": "execute_compat_tests"
    }

    gui_help_tooltips = {

        "LabelCompatTestsHelp": """
1. DuFi cannot process files in Unicode (UTF-8, UTF-16, UTF-32).
    These files must be converted into ones in a single-byte encoding.
    Windows-1251 (CP1251) is a good choice for almost all Cyrillic texts.
2. Files must have unified style of line endings: CR+LF (Windows) or LF (Unix).
3. Each file must end with line ending characters. Otherwise, it indicates
    the file was not extracted completely (extraction process was interrupted).
These checks can be turned off if all the files successfully passed them before.
""",

        "LabelCyrillicHelp": """
If checked, better Cyrillyc-only encodings detection enabled.
If not checked, non-Cyrillyc encodings can be detected.
""",

    }

    ############################################################################

    CHECK_EOL_LIMIT = 50_000

    @classmethod
    def run(cls, args):
        for file in process_files(args):
            try:
                valid, fixable = cls._check_file(file, args)
            except DiagnosticsError as e:
                echo("ERROR: {}".format(e))
                return 1

            if valid:
                echo("(^_^) file is valid")
            elif fixable:
                echo("(-_-) file is corrupted; can be repaired automatically")
            else:
                echo("(X_X) file is corrupted; should be repaired manually")

        echo("All files are processed. See *.dufireport for details.")

    @classmethod
    def _check_file(cls, file, args):
        # check eof

        if not args.exclude_compat_tests:
            with open(file, "rb") as fp:
                fp.seek(-1, os.SEEK_END)

                last_char = fp.read(1)

            if last_char == b"\0":
                raise DiagnosticsError("file ends with 0x00 character (unicode?)")

            if last_char != b"\n":
                raise DiagnosticsError("file does not end with EOL sequence")

            # check eol
            if cls._get_eol_style(file) not in ("windows", "unix"):
                raise DiagnosticsError("file contains both Windows and Unix EOLs")

            # check encoding
            encoding = detect_encoding(
                file, args.lines_limit, cyrillic=not args.non_cyrillic)

            if encoding.lower().startswith("utf"):
                raise DiagnosticsError("file has an Unicode encoding")

        # count separators
        report_file = file + ".dufireport"
        file_size = os.path.getsize(file)

        with open(file, "rb") as fpi, \
                open(report_file, "w") as fpo:
            if args.with_qualifier:
                return count_seps_with_quotes(
                    fpi, fpo, file_size, get_separator(args), b'"'[0], -1)
            else:
                return count_seps_no_quoting(
                    fpi, fpo, file_size, get_separator(args), -1)

    @classmethod
    def _get_eol_style(cls, fname):
        with open(fname, "rb") as fp:
            eol_win = False
            eol_unix = False

            pc = None
            i = 0

            while True:
                cc = fp.read(1)

                if not cc:
                    break

                if cc == b"\n":
                    if pc == b"\r":
                        eol_win = True

                        if eol_unix:
                            return "mixed"

                    else:
                        eol_unix = True

                        if eol_win:
                            return "mixed"

                    i += 1

                    if i >= cls.CHECK_EOL_LIMIT:
                        break

                pc = cc

            if eol_win:
                return "windows"

            if eol_unix:
                return "unix"

            return "unknown"

    ############################################################################

    @classmethod
    def _add_arguments(cls, parser):
        cls._add_csv_arguments(parser)
        parser.add_argument(
            "-x", "--exclude-compat-tests",
            action="store_true",
            help="do not perform checks (encoding, EOL, EOF)",
        )
        parser.add_argument(
            "-i", "--non-cyrillic",
            action="store_true",
            help=("csv files have characters different from characters that "
                  "belong to Latin or Cyrillic alphabets"),
        )
        parser.add_argument(
            "-m", "--lines-limit",
            type=int,
            default=1000,
            metavar="N",
            help=("maximum number of lines which will be used to detect file "
                  "encoding (default: 1000)"),
        )
        cls._add_files_arguments(parser)

    ############################################################################

    @classmethod
    def _validate_cmd_args(cls, var):
        cls._validate_files(var)
        cls._validate_separator(var)

    ############################################################################

    @classmethod
    def _get_cmd_args(cls, var):
        args = []
        args.extend(cls._get_cmd_args_separator(var))

        if var.with_quotes:
            args.append("--with-qualifier")

        if not var.execute_compat_tests:
            args.append("--exclude-compat-tests")

        if not var.cyrillic:
            args.append("--non-cyrillic")

        return args
