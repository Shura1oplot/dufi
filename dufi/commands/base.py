# [SublimeLinter @python:3]

import sys
import re

from .arghelpers import type_single_byte, FakeParser


class dufi_commands_meta(type):

    def __iter__(cls):
        return iter(cls.commands)

    def __getitem__(cls, name):
        return cls.get_by_name_gui(name)


class dufi_commands(list, metaclass=dufi_commands_meta):

    commands = []

    @classmethod
    def get_names(cls):
        cmd_lst = [cmd for cmd in cls.commands if cmd.gui_command]
        cmd_lst.sort(key=lambda x: x.gui_order)
        return [cmd.gui_command for cmd in cmd_lst]

    @classmethod
    def get_by_name_gui(cls, name):
        for cmd in cls.commands:
            if cmd.gui_command == name:
                return cmd

        raise ValueError(name)

    @classmethod
    def get_by_name_cli(cls, name):
        for cmd in cls.commands:
            if cmd.cli_command == name:
                return cmd

        raise ValueError(name)

    @classmethod
    def get_default(cls):
        default = {"separator": "  | (vertical bar)"}

        for cmd in cls.commands:
            default.update(cmd.gui_default)

        return default

    @classmethod
    def get_switches(cls):
        switches = {}

        for cmd in cls.commands:
            switches.update(cmd.gui_switches)

        return switches


class InvalidCommandArgs(Exception):

    def __init__(self, error_text):
        super(InvalidCommandArgs, self).__init__()

        self.error_text = error_text


class CommandMeta(type):

    def __repr__(cls):
        return "<Command({})>".format(cls.gui_command)


class Command(object, metaclass=CommandMeta):

    cli_command = None
    cli_command_aliases = ()
    cli_command_help = None
    cli_files_required = True

    gui_order = None
    gui_command = None
    gui_description = "You can find the program documentation on DA Wiki."
    gui_files_info_label_id = None
    gui_info_message_widget = None

    gui_variables = None
    gui_default = {}
    gui_switches = {}

    gui_help_tooltips = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        dufi_commands.commands.append(cls)
        dufi_commands.commands.sort(key=lambda cmd: (cmd.cli_command is None,
                                                     cmd.cli_command))

    ############################################################################

    @classmethod
    def get_name(cls, app):
        return cls.gui_command

    ############################################################################

    @classmethod
    def run(cls, args):
        pass

    ############################################################################

    @classmethod
    def add_args_parser_to(cls, subparsers):
        if cls.cli_command is None:
            return

        parser = subparsers.add_parser(
            cls.cli_command, aliases=cls.cli_command_aliases, help=cls.cli_command_help)
        cls._add_arguments(parser)
        parser.set_defaults(command=cls.run)

    @classmethod
    def _add_arguments(cls, parser):
        pass

    @staticmethod
    def _add_csv_arguments(p, qualifier=True):
        p.add_argument(
            "-s", "--separator",
            type=type_single_byte,
            default=",",
            metavar="CHAR",
            help="character that separates fields in a row (default: ',')",
        )
        p.add_argument(
            "-T", "--tab-separator",
            action="store_true",
            help="fields separated by tab character",
        )

        if qualifier:
            p.add_argument(
                "-q", "--with-qualifier",
                action="store_true",
                help="values have double quotes around",
            )

    @staticmethod
    def _add_coding_arguments(p):
        p.add_argument(
            "-f", "--from-code",
            required=True,
            metavar="ENCODING",
            help="convert characters from encoding",
        )
        p.add_argument(
            "-t", "--to-code",
            required=True,
            metavar="ENCODING",
            help="convert characters to encoding",
        )

    @staticmethod
    def _add_files_arguments(p):
        p.add_argument(
            "-l", "--list",
            action="store_true",
            help="files to process listed in the files given",
        )
        p.add_argument(
            "files",
            nargs="+",
            metavar="FILE",
            help="CSV files to process",
        )

    ############################################################################

    @classmethod
    def init_gui(cls, app):
        cls._attach_tooltips(app)
        cls._init_gui(app)

    @classmethod
    def _attach_tooltips(cls, app):
        for object_id, text in cls.gui_help_tooltips.items():
            app.attach_tooltip(object_id, text.strip())

        if cls.gui_files_info_label_id:
            app.attach_files_info_tooltip(cls.gui_files_info_label_id)

    @classmethod
    def _init_gui(cls, app):
        pass

    ############################################################################

    @classmethod
    def validate_cmd_args(cls, app):
        var = app.var

        if not var.files:
            raise InvalidCommandArgs(
                ('No files selected! Use "Add..." button to select files or '
                 "drag-and-drop them into the program window."))

        cls._validate_cmd_args(var)

    @classmethod
    def _validate_separator(cls, var):
        if not re.match(r"^ *(<TAB>|.( \(.*\))?) *$", var.separator):
            raise InvalidCommandArgs("Separator must be a single character!")

    @classmethod
    def _validate_files(cls, var):
        if not var.files:
            raise InvalidCommandArgs(
                ('No files selected! Use "Add..." button to select files or '
                 "drag-and-drop them into the program window."))

    @classmethod
    def _validate_cmd_args(cls, var):
        pass

    ############################################################################

    @classmethod
    def get_cmd_args(cls, app):
        if cls.cli_command is None:
            raise ValueError("{} is not executable".format(cls.gui_command))

        args = [sys.executable, ]

        if not getattr(sys, "frozen", False):
            args.append(sys.argv[0])

        args.append(cls.cli_command)
        args.extend(cls._get_cmd_args(app.var))
        args.extend(["--list", "--", "-"])
        return args

    @classmethod
    def _get_cmd_args_separator(cls, var):
        separator = var.separator.strip()

        if separator == "<TAB>":
            return ["--tab-separator", ]
        else:
            return ["--separator", separator[0]]

    @classmethod
    def _get_cmd_args(cls, var):
        return []

    ############################################################################

    @classmethod
    def get_command_schema(cls):
        p = FakeParser()
        cls.add_args_parser_to(p)
        return p.args
