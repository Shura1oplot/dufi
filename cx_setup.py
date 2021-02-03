# [SublimeLinter @python:3]

import sys
import os
from cx_Freeze import setup, Executable


if sys.version_info[:2] != (3, 8):
    raise Exception("Python 3.8 required!")


# https://cx-freeze.readthedocs.io/en/latest/distutils.html
build_exe_options = {
    "build_exe": os.path.abspath("build_exe"),
    "packages": ["decimal", "gzip", "idna", "lxml"],  # lxml._elementpath?
    "excludes": ["Tkinter", "numpy", "pandas", "multiprocessing", "_ssl"],
    "include_msvcr": True,
}

target = Executable(
    script="dufi.py",
    base="Win32GUI",
    icon="dufi\\gui\\resources\\dufi-gui-exe.ico",
)

setup(
    name="dufi",
    version="0.9.10",
    description="Dump Fixer Tools",
    options={"build_exe": build_exe_options},
    executables=[target, ],
)
