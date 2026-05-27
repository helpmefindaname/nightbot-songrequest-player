@echo off
cd /d %~dp0
uv sync
uv run songrequest
pause