# [SublimeLinter @python:3]

import os
import logging
import shutil
import tempfile
import psutil

import tika.tika
import tika.parser

from .base import Command
from .arghelpers import format_file_path, process_files
from ..utils import get_resources_path

logging.getLogger("tika.tika").setLevel(logging.ERROR)


class TikaCommand(Command):

    cli_command = "tika"
    cli_command_aliases = ()
    cli_command_help = "extract text from all kind of documents"

    ############################################################################

    @classmethod
    def run(cls, args):
        for fname in ("tika-server.jar", "tika-server.jar.md5"):
            dest_file = os.path.join(tempfile.gettempdir(), fname)

            if not os.path.exists(dest_file):
                shutil.copy2(get_resources_path(fname), dest_file)

        for file in process_files(args):
            file = os.path.abspath(file)
            file_out = os.path.abspath(format_file_path(args.output, file))
            os.makedirs(os.path.dirname(file_out), exist_ok=True)
            parsed = tika.parser.from_file(file)

            with open(file_out, "w", encoding="utf-8") as fp:
                fp.write(parsed["content"])

        tikajar = os.path.abspath(
            os.path.join(tempfile.gettempdir(), "tika-server.jar")).lower()

        for proc in psutil.process_iter():
            try:
                if os.path.basename(proc.exe()).lower() == "java.exe" \
                        and any(tikajar == x.lower() for x in proc.cmdline()):
                    proc.terminate()
                    break
            except psutil.AccessDenied:
                continue

    ############################################################################

    @classmethod
    def _add_arguments(cls, parser):
        parser.add_argument(
            "-o", "--output",
            default="!\\!.txt",
            metavar="FILE_MASK",
            help="specify output files mask (default: !\\!.txt)"
        )
        cls._add_files_arguments(parser)
