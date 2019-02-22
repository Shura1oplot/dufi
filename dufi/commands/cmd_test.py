# [SublimeLinter @python:3]

import time
import argparse

from .base import Command
from ..utils import echo


class TestCommand(Command):

    cli_command = "test"
    cli_command_aliases = ()
    cli_command_help = argparse.SUPPRESS  # http://bugs.python.org/issue22848
    cli_files_required = False

    ############################################################################

    @classmethod
    def run(cls, args):
        echo("Processing 1/3: a.txt")

        for i in range(101):
            echo("Progress: {}%".format(i))
            time.sleep(0.05)

        echo("Processing 2/3: b.txt")

        for i in range(101):
            echo("Progress: {}%".format(i))

            if i == 50:
                raise RuntimeError("atata")

            time.sleep(0.01)

        echo("Processing 3/3: c.txt")

        for i in range(101):
            echo("Progress: {}%".format(i))
            time.sleep(0.01)

    ############################################################################

    @classmethod
    def _add_arguments(cls, parser):
        pass
