# [SublimeLinter @python:3]

from ..utils import echo


def patch(csv_file, patch_file, reverse=False, dry_run=False, force=False):
    read_count = 0
    applied_count = 0

    with open(csv_file, "r+b") as fp_csv, \
            open(patch_file, "r") as fp_patch:
        for line in fp_patch:
            if line.startswith("#"):
                continue

            try:
                offset, expected_code, replace_code = map(int, line.rstrip().split(":"))
            except ValueError:
                echo("ERROR: invalid patch file")
                return 1

            if reverse:
                expected_code, replace_code = replace_code, expected_code

            fp_csv.seek(offset)
            char = fp_csv.read(1)

            if not char:
                echo("ERRPR: patch is not applicable")
                return 1

            char_code = ord(char)
            read_count += 1

            if char_code == replace_code:
                continue

            if char_code != expected_code:
                echo("ERROR: unexpected char at", offset)

                if not force:
                    return 1

            fp_csv.seek(offset)

            if not dry_run:
                fp_csv.write(bytes((replace_code, )))

            applied_count += 1

    echo("Replacements applied: {} / {}".format(applied_count, read_count))
    return 0
