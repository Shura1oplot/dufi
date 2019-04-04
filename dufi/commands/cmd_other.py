# [SublimeLinter @python:3]

import sys

from .base import dufi_commands, Command, InvalidCommandArgs


class OtherCommand(Command):

    cli_command = None
    cli_command_aliases = None
    cli_command_help = None

    gui_order = 12
    gui_command = "Other..."
    gui_description = "All available DuFi commands."
    gui_files_info_label_id = "LabelOtherFilesInfo"
    gui_info_message_widget = None

    ############################################################################

    @classmethod
    def _init_gui(cls, app):
        cb = app.builder.get_object("ComboboxOtherCommands")
        cb["values"] = [cmd.cli_command for cmd in dufi_commands if cmd.cli_command]
        cb.current(0)
        app.on_other_command_selected()

    ############################################################################

    @classmethod
    def get_name(cls, app):
        cmd = dufi_commands.get_by_name_cli(app.var.other_command)
        return cmd.gui_command or cmd.cli_command

    ############################################################################

    @classmethod
    def validate_cmd_args(cls, app):
        if not app.var.other_command:
            raise InvalidCommandArgs("Command not specified!")

        command = app.var.other_command
        dufcmd = dufi_commands.get_by_name_cli(command)

        if dufcmd.cli_files_required:
            cls._validate_files(app.var)

    ############################################################################

    @classmethod
    def get_cmd_args(cls, app):
        args = [sys.executable, ]

        if not getattr(sys, "frozen", False):
            args.append(sys.argv[0])

        command = app.var.other_command
        dufcmd = dufi_commands.get_by_name_cli(command)
        bool_args = {arg for arg, spec, _ in dufcmd.get_command_schema()
                     if spec.get("action") == "truefalse"}

        args.append(command)

        for arg, value in app.get_other_command_args():
            if arg in bool_args:
                if value == "Yes":
                    args.append(arg)

            elif value in ("''", '""'):
                if arg.startswith("-"):
                    args.append(arg)

                args.append("")

            elif value:
                if arg.startswith("-"):
                    args.append(arg)

                args.append(value)

        if app.var.files:
            args.extend(["--list", "--", "-"])

        return args
