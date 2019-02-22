@ECHO OFF

CALL config.bat

SET "DIST=releases\dufi_%VERSION%.7z"
IF EXIST "%DIST%" DEL "%DIST%"
7z a "%DIST%" "dufi-%VERSION%"
