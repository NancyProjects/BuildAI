@echo off
cd /d "%~dp0"
py -3 -m venv .venv
if errorlevel 1 (echo Install Python 3.12 or newer first.& pause & exit /b 1)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (pause & exit /b 1)
.venv\Scripts\python.exe manage.py migrate
pause
