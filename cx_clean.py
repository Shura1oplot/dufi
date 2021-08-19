# [SublimeLinter @python:3]

import sys
import shutil
from pathlib import Path


def main(argv=sys.argv):
    if not Path("build_exe").exists():
        raise Exception("directory build_exe not found!")

    dll_path = Path("build_exe/lib")

    for file in Path("build_exe").glob("**/*.dll"):
        if file.parent == dll_path:
            continue

        target_dll = dll_path / file.name

        if target_dll.exists():
            file.unlink()
        else:
            file.rename(target_dll)

    Path("build_exe/lib/python38.dll").rename("build_exe/python38.dll")

    for mask in ("*.c", "*.pyx", "*.pxx"):
        for file in Path("build_exe/lib/dufi/commands").glob(mask):
            file.unlink()

    shutil.rmtree("build_exe/lib/distutils/command")
    shutil.rmtree("build_exe/lib/tkinter/tk8.6/demos")

    Path("build_exe/lib/libcrypto-1_1-x64.dll").unlink()

    print("cx_clean.py: done!")


if __name__ == "__main__":
    sys.exit(main())
