@echo off
setlocal EnableDelayedExpansion

:: Default log level
set LOG_LEVEL=INFO

:: Parse command line arguments
:parse_args
if "%~1"=="" goto end_parse_args
if "%~1"=="--log-level" (
    set LOG_LEVEL=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-d" (
    set LOG_LEVEL=DEBUG
    shift
    goto parse_args
)
if "%~1"=="--debug" (
    set LOG_LEVEL=DEBUG
    shift
    goto parse_args
)
shift
goto parse_args
:end_parse_args

echo Log level set to %LOG_LEVEL%

echo Checking for virtual environment...

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing requirements...
pip install -r requirements.txt

:: Set log level environment variable
set LOG_LEVEL=%LOG_LEVEL%

:: Load HOST and PORT from .env file
echo Loading environment variables from .env file...
if exist .env (
    for /f "tokens=*" %%a in ('type .env ^| findstr /v "^#"') do (
        set %%a
    )
) else (
    echo No .env file found. Using default settings.
    set HOST=0.0.0.0
    set PORT=8777
)

echo Using HOST=%HOST% and PORT=%PORT%

:: Kill any existing process using the same port
echo Checking for processes using port %PORT%...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%PORT%"') do (
    echo Found process with PID %%a using port %PORT%. Killing it...
    taskkill /F /PID %%a
    timeout /t 1 /nobreak >nul
)

echo Starting the server...
uvicorn main:app --host %HOST% --port %PORT% --reload 