@echo off

for %%x in (*.ui) do call :body %%x
goto :eof

:body
set pyname_tmp=%~n1
set pyname=%pyname_tmp:-=_%ui
(
    echo # -*- coding: utf-8 -*-
    echo.
    echo %pyname% = '''\
) >"%pyname%.py"
type "%1">>"%pyname%.py"
echo '''>>"%pyname%.py"
goto :eof
