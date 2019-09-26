@ECHO OFF

CALL config.bat

CALL "%VCVARS32%"

MKDIR build

CD build
midl "%SDK_DIR%\um\ShObjIdl_core.idl" /tlb "ShObjIdl_core.tlb" /target NT60
midl "%SDK_DIR%\um\ShObjIdl.idl" /tlb "ShObjIdl.tlb" /target NT60
CD ..

IF ERRORLEVEL 1 GOTO :EOF
