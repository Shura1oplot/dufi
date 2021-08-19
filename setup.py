# [SublimeLinter @python:3]

import pathlib
from setuptools import setup, find_packages
from Cython.Build import cythonize
import cypp


try:
    with open("README.rst") as readme_file:
        readme = readme_file.read()
except FileNotFoundError:
    readme = ""

try:
    with open("HISTORY.rst") as history_file:
        history = history_file.read()
except FileNotFoundError:
    history = ""


requirements = []

setup_requirements = []

# test_requirements = []


def _preprocess_pyx(pattern):
    for file in pathlib.Path(__file__).parent.glob(pattern):
        file_out = file.with_suffix(".pyx")

        with open(file, "r", encoding="utf-8") as fpi, \
                open(file_out, "w", encoding="utf-8") as fpo:
            cypp.run(fpi, fpo)

    return pattern.replace(".pxx", ".pyx")


setup(
    author="Alexander Gordeyev",
    author_email="s0meuser@yandex.ru",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Programming Language :: Cython",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8", 
   ],
    description="Dump Fixer Tools",
    entry_points={
        "console_scripts": [
            "dufi = dufi.cli:main",
        ],
        "gui_scripts": [
            "dufi-gui = dufi.gui:main"
        ]
    },
    install_requires=requirements,
    license="MIT License",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords="dufi",
    name="dufi",
    packages=find_packages(include=["dufi", ]),
    setup_requires=setup_requirements,
    # test_suite="tests",
    # tests_require=test_requirements,
    url="https://github.com/Shura1oplot/dufi",
    version="0.9.10",
    zip_safe=False,
    ext_modules=cythonize(_preprocess_pyx("dufi/commands/*.pxx"), language_level="3"),
)
