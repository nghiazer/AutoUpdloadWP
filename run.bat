@echo off
REM Papercraft Automation Runner Script

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Run the main script
python main.py %*
