# [SublimeLinter @python:3]

import os
import re
import datetime
import argparse

from . import workingtime

from ..base import Command, InvalidCommandArgs
from ..arghelpers import GUIOpt, process_files
from ...utils import get_base_path


class WorkingHoursCommand(Command):

    cli_command = "working-time"
    cli_command_aliases = ("wh", )
    cli_command_help = "calculate difference between given dates considering only working time"

    gui_order = 11
    gui_command = "Working Time"
    gui_description = "Working time calculator (DEPRECATED)."
    gui_files_info_label_id = "LabelWorkingTimeFilesInfo"
    gui_info_message_widget = "MessageWorkingTimeInfo"

    _weekdays_vars = ("wt_1", "wt_2", "wt_3", "wt_4", "wt_5", "wt_6", "wt_7")
    gui_variables = _weekdays_vars

    gui_help_tooltips = {

        "LabelWorkingTimeFilesHelp2": """
1. YYYY-mm-dd HH:MM:SS.µs: {0:%Y-%m-%d %H:%M:%S.%f}
2. YYYY-mm-dd HH:MM:SS: {0:%Y-%m-%d %H:%M:%S}
3. dd-mm-YYYY HH:MM:SS: {0:%d.%m.%Y %H:%M:%S}
4. dd-mm-YYYY HH:MM: {0:%d.%m.%Y %H:%M}
""".format(datetime.datetime.today())

    }

    _weekdays = "monday tuesday wednesday thursday friday saturday sunday"
    _default_schedule = "09:00-12:00,13:00-18:00"
    _date_parse_masks = ("%Y-%m-%d %H:%M:%S.%f",
                         "%Y-%m-%d %H:%M:%S",
                         "%d.%m.%Y %H:%M:%S",
                         "%d.%m.%Y %H:%M")

    ############################################################################

    @staticmethod
    def _validate_time_range(s):
        if not isinstance(s, str):
            return False

        return bool(re.match(
            r"^default|{0}-{0}(?:,{0}-{0})*$".format(r"\d\d:\d\d(?:\d\d:\d\d)?"),
            s.strip(), flags=re.I))

    ############################################################################

    @staticmethod
    def _read_date_list(file):
        result = []

        for line in open(file):
            line = line.strip()

            if not line:
                continue

            if line.startswith("#"):
                continue

            try:
                value = datetime.datetime.strptime(line, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("cannot parse value: {!r}".format(line))

            result.append(value)

        return result

    @classmethod
    def run(cls, args):
        workdays = {}

        for i, x in enumerate(cls._weekdays.split(), 1):
            v = getattr(args, x, None)

            if not v:
                continue

            workdays[i] = v

        holidays = []

        if args.holidays:
            holidays = cls._read_date_list(args.holidays)

        half_holidays = []

        if args.half_holidays:
            half_holidays = cls._read_date_list(args.half_holidays)

        for file in process_files(args):
            file_dir = os.path.dirname(file)
            file_name, file_ext = os.path.splitext(os.path.basename(file))
            file_out = os.path.join(file_dir, "{}_OUT{}".format(file_name, file_ext))

            # TODO: progress?
            with open(file) as fpi, open(file_out, "w") as fpo:
                for line in fpi:
                    line = line.strip()

                    if not line:
                        continue

                    try:
                        date_from_str, date_to_str = line.split("\t")
                    except ValueError:
                        raise ValueError("cannot parse: {!r}".format(line))

                    for mask in cls._date_parse_masks:
                        try:
                            date_from = datetime.datetime.strptime(date_from_str, mask)
                            date_to = datetime.datetime.strptime(date_to_str, mask)
                        except ValueError:
                            pass
                        else:
                            break
                    else:
                        raise ValueError("cannot parse: {!r}".format(line))

                    dt = workingtime.get_working_time(
                        date_from=date_from,
                        date_to=date_to,
                        workdays=workdays,
                        default_schedule=None,
                        holidays=holidays,
                        half_holidays=half_holidays)

                    fpo.write("{}\t{}\n".format(line, dt.total_seconds()))

    ############################################################################

    @classmethod
    def _time_ranges_type(cls, s):
        s = s.strip().lower()

        if not s:
            return None

        if not cls._validate_time_range(s):
            raise argparse.ArgumentTypeError("invalid schedule value")

        if s == "default":
            return cls._time_ranges_type(cls._default_schedule)

        ranges = []

        for pair in s.split(","):
            ranges.append(tuple(datetime.time(*(int(x) for x in tm.split(":")))
                                for tm in pair.split("-")))

        return ranges

    @classmethod
    def _add_arguments(cls, parser):
        guiopt = GUIOpt(parser)

        parser.add_argument(
            "-d", "--default-schedule",
            type=cls._time_ranges_type,
            default=cls._time_ranges_type("default"),
            metavar="HH:MM-HH:MM[,...]",
            help="specify default workday schedule (default: {})".format(
                cls._default_schedule),
            **guiopt(default=cls._default_schedule))

        for i, x in enumerate(cls._weekdays.split(" "), 1):
            parser.add_argument(
                "-{}".format(i), "--{}".format(x),
                type=cls._time_ranges_type,
                const=cls._time_ranges_type("default") if i <= 5 else "",
                nargs="?",
                metavar="default|HH:MM-HH:MM[,...]",
                help="specify schedule for {}".format(x))

        parser.add_argument(
            "-i", "--holidays",
            metavar="FILE",
            help="specify file with list of holidays",
            **guiopt(action="browse_file"))

        parser.add_argument(
            "-j", "--half-holidays",
            metavar="FILE",
            help="specify file with list of half-holidays",
            **guiopt(action="browse_file"))

        cls._add_files_arguments(parser)

    ############################################################################

    @classmethod
    def _validate_cmd_args(cls, var):
        cls._validate_files(var)

        for x in cls._weekdays_vars:
            v = var[x]

            if v and not cls._validate_time_range(v):
                raise InvalidCommandArgs(
                    "Invalid time range value: {!r}".format(v))

    ############################################################################

    @classmethod
    def _get_cmd_args(cls, var):
        args = []

        for i in range(1, 8):
            args.append("-{}".format(i))
            args.append(var["wt_{}".format(i)].strip())

        args.append("--holidays")

        base_path = get_base_path()
        args.append(os.path.join(base_path, "holidays.txt"))

        args.append("--half-holidays")
        args.append(os.path.join(base_path, "half-holidays.txt"))

        return args
