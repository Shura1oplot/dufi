Dump Fixer Tools
================

Dump Fixer Tools are a set of useful utilities that helps you to deal with rukozhopy data extractions.

Build Dependencies
==================
1. Windows 10 x64
1. Python 3.7
1. Microsoft Visual Studio 2019 Community with "Desktop development with C++" components
1. Python modules from requirements.txt and requirements_dev.txt

How to build
============

Method 1 (simple):
1. Run command prompt in admin mode
1. Activate conda environment
1. build_all.bat

Method 2:
1. Run command prompt in user mode
1. Activate conda environment
1. clean.py
1. configure.py
1. build_lib.bat
1. build_tlb.bat
1. Run command prompt in admin mode
1. Activate conda environment
1. gen_comtypes_cache.py
1. Switch back to command prompt in user mode
1. build_exe.bat
1. build_dist.bat
