# [SublimeLinter @python:3]

import os
import importlib

from .base import dufi_commands, InvalidCommandArgs

from . import (
    # cli commands
    cmd_test,
    cmd_iconv,
    cmd_patch,
    cmd_concat,
    cmd_sample,
    cmd_tika,
    cmd_xml2db_schema,
    cmd_xml2db_scripts,
    cmd_xml2db_convert,

    # gui commands
    cmd_diagnostics,
    cmd_repair,
    cmd_merge_column,
    cmd_oracle_fix,
    cmd_convert,
    cmd_cr_to_space,
    cmd_count_lines,
    cmd_join_rows,
    cmd_genscript,
    cmd_excel,
    cmd_workingtime,
    cmd_xml2csv,
    cmd_other,
)

# def _load_commands():
#     for file in os.listdir(os.path.dirname(__file__)):
#         if file.startswith("cmd_") and file.endswith(".py"):
#             modulename = "dufiimpl.commands.{}".format(
#                 os.path.basename(file).replace(".py", ""))
#             importlib.import_module(modulename)


# _load_commands()
