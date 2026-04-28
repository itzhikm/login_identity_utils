@echo off
rem Run main.py with environment variables loaded from the project's .env file.

setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_ROOT=%%~fI"

set "ENV_FILE=%PROJECT_ROOT%\.env"
if not exist "%ENV_FILE%" (
    echo deploy_db.cmd: missing env file at "%ENV_FILE%" 1>&2
    exit /b 1
)

for /f "usebackq eol=# tokens=1,* delims==" %%a in ("%ENV_FILE%") do (
    if not "%%a"=="" set "%%a=%%b"
)

set "PYTHON=%PROJECT_ROOT%\.venv\Scripts\python.exe"
if not exist "%PYTHON%" set "PYTHON=python"

cd /d "%PROJECT_ROOT%"
"%PYTHON%" main.py %*
exit /b %ERRORLEVEL%
