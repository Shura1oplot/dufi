# [SublimeLinter @python:3]

import sys
import os
from pathlib import Path
import platform
import ctypes


DUFI_VERSION = "0.9.10"

TCL_VERSION = "8.6"

SDK_BASE_DIR = "%ProgramFiles(x86)%\\Windows Kits\\10\\Include"
VC_DIR = "%ProgramFiles(x86)%\\Microsoft Visual Studio\\2017\\Community\\VC\\Auxiliary\\Build"


def main(argv=sys.argv):
    # Check permissions

    if len(argv) > 1 and argv[1] == "--check-admin":
        if not ctypes.windll.shell32.IsUserAnAdmin():
            raise ValueError("Should be run with admin rights!")

    # Check dependencies

    if sys.version_info[:2] != (3, 6):
        print("Warning: python 3.6 is required to build exe!")

    buildenv = platform.uname()

    if buildenv.system != "Windows" \
            or buildenv.release != "10" \
            or buildenv.machine != "AMD64":
        raise Exception("Windows 10 x64 required!")

    for file in ("vcvars32.bat", "vcvars64.bat"):
        if not (Path(os.path.expandvars(VC_DIR)) / file).exists():
            raise Exception("Visual Studio 2017 Community required!")

    # Create config.bat

    python_dir = Path(sys.executable).parent
    tcl_dir = python_dir / "tcl" / "tcl{}".format(TCL_VERSION)
    tk_dir = python_dir / "tcl" / "tk{}".format(TCL_VERSION)

    if not tcl_dir.exists() or not tk_dir.exists():
        raise Exception("tcl/tk not found!")

    sdk_dir = Path(os.path.expandvars(SDK_BASE_DIR))
    sdk_versions = [x.name for x in sdk_dir.iterdir() if x.is_dir()]
    sdk_versions.sort(reverse=True)

    if not sdk_versions:
        raise Exception("Windows Kits not found!")

    with open("config.bat", "w", encoding="ascii") as fp:
        fp.write('@SET "TCL_LIBRARY={}"\n'.format(tcl_dir))
        fp.write('@SET "TK_LIBRARY={}"\n'.format(tk_dir))
        fp.write('@SET "VCVARS32={}\\vcvars32.bat"\n'.format(VC_DIR))
        fp.write('@SET "VCVARS64={}\\vcvars64.bat"\n'.format(VC_DIR))
        fp.write('@SET "SDK_VERSION={}"\n'.format(sdk_versions[0]))
        fp.write('@SET "SDK_DIR={}\\%SDK_VERSION%"\n'.format(SDK_BASE_DIR))
        fp.write('@SET "VERSION={}"\n'.format(DUFI_VERSION))

    print("configure.py: done!")


if __name__ == "__main__":
    sys.exit(main())
