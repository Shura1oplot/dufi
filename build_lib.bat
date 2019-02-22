@ECHO OFF

CALL config.bat

CALL "%VCVARS64%"
python setup.py build_ext --inplace
IF ERRORLEVEL 1 GOTO :EOF
