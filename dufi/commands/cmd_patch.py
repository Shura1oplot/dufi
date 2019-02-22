# [SublimeLinter @python:3]

from .base import Command
from .patch import patch
from .arghelpers import GUIOpt


class PatchCommand(Command):

    cli_command = "patch"
    cli_command_aliases = ()
    cli_command_help = "apply or revert dufipatch"
    cli_files_required = False

    ############################################################################

    @classmethod
    def run(cls, args):
        return patch(args.csv_file, args.patch_file, args.reverse,
                     args.dry_run, args.force)

    ############################################################################

    @classmethod
    def _add_arguments(cls, parser):
        guiopt = GUIOpt(parser)

        parser.add_argument(
            "-D", "--dry-run",
            action="store_true",
            help=("print the results of applying the patch without actually "
                  "changing the file"),
        )
        parser.add_argument(
            "-R", "--reverse",
            action="store_true",
            help="reverse applied patch",
        )
        parser.add_argument(
            "-f", "--force",
            action="store_true",
            help="continue patching even if an unexpected char is found",
        )
        parser.add_argument(
            "-r", "--retry",
            action="store_true",
            help=("wait and retry to open the dump file if it is locked by other "
                  "process"),
        )
        parser.add_argument(
            "patch_file",
            help="patch to apply",
            **guiopt(action="browse_file")
        )
        parser.add_argument(
            "csv_file",
            help="csv file to process",
            **guiopt(action="browse_file")
        )
