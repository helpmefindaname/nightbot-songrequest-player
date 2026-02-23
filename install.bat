@echo off
cd /d %~dp0

echo Checking for uv...
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo uv not found. Installing uv...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
    for /f "tokens=2*" %%A in ('reg query HKCU\Environment /v Path 2^>nul') do set "USERPATH=%%B"
    set "PATH=%USERPATH%;%PATH%"
) else (
    echo uv already installed.
)

echo.
echo Running uv sync to create virtual environment...
uv sync
if %errorlevel% neq 0 (
    echo uv sync failed.
    pause
    exit /b 1
)

echo.
echo Setup complete!
pause