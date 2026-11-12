@echo off
rem Runs studio scripts with the uv-managed Python (venv executables are blocked by
rem Windows App Control on this PC) and the local .deps folder.
setlocal
set "PY=%APPDATA%\uv\python\cpython-3.12.16-windows-x86_64-none\python.exe"
set "PYTHONPATH=%~dp0.deps;%~dp0"
set "PYTHONIOENCODING=utf-8"
if "%1"=="build" (shift & "%PY%" "%~dp0build.py" %2 %3 %4 %5 & goto :eof)
if "%1"=="voices" ("%PY%" -m engine.tts voices & goto :eof)
if "%1"=="shared" ("%PY%" -m engine.tts shared %2 & goto :eof)
"%PY%" %*
