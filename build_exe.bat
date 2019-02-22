@ECHO OFF

CALL config.bat

IF EXIST build_exe RMDIR /S /Q build_exe
python cx_setup.py build_exe
python cx_clean.py

CALL "%VCVARS32%"
mt.exe -nologo -manifest "dufi.exe.manifest" -outputresource:"build_exe\dufi.exe;#1"
REN build_exe "dufi-%VERSION%"
