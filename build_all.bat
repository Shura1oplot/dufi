@ECHO OFF

python clean.py
python configure.py --check-admin
IF ERRORLEVEL 1 GOTO :EOF

CALL build_lib.bat
CALL build_tlb.bat

python gen_comtypes_cache.py
IF ERRORLEVEL 1 GOTO :EOF

CALL build_exe.bat
CALL build_dist.bat
