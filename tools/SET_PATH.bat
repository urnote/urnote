:: PATH-ADD - add a path to user path environment variable

@echo off
setlocal

:: set user path
set ok=0
for /f "skip=2 tokens=3*" %%a in ('reg query HKCU\Environment /v PATH') do if [%%b]==[] ( setx PATH "%%~a;%cd%" && set ok=1 ) else ( setx PATH "%%~a %%~b;%cd%" && set ok=1 )
if "%ok%" == "0" setx PATH "%cd%"

:end
endlocal
echo.