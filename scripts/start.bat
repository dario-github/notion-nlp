@echo off

color 0a

:main
echo 1. English
echo 2. 简体中文

echo=
set /p language=Choose Language / 选择语言:

if %language% == 1 && (start cmd call .\English.bat) || goto main
if %language% == 2 && (start cmd call .\中文.bat) || goto main