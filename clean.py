# [SublimeLinter @python:3]

import sys
from pathlib import Path
import shutil


def main(argv=sys.argv):
    for x in Path().glob("**/__pycache__"):
        if x.is_dir():
            shutil.rmtree(x)

    for x in Path().glob("**/*.pyc"):
        if x.is_file():
            x.unlink()

    if Path("build").exists():
        shutil.rmtree("build")

    if Path("build_exe").exists():
        shutil.rmtree("build_exe")

    for mask in ("*.c", "*.pyd", "*.pyx"):
        for file in Path("dufi/commands").glob(mask):
            file.unlink()

    for d in Path().glob("dufi-*"):
        if d.is_dir():
            shutil.rmtree(d)

    print("clean.py: done!")


if __name__ == "__main__":
    sys.exit(main())
