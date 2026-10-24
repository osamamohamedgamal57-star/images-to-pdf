@echo off
rem Double-click this file to start the bot. Keep the window open while the bot is running.
cd /d "%~dp0"
title Images to PDF Bot

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found. Install it from https://www.python.org/downloads/
    echo and tick "Add python.exe to PATH" during the installation.
    pause
    exit /b 1
)

rem First run: create the .env file and let the user fill it in
if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo First run: Notepad will open the .env file.
    echo Paste your BOT_TOKEN and ADMIN_ID, save the file, and close Notepad.
    notepad ".env"
)

rem Install the libraries only if something is missing
python -c "import telegram, PIL, dotenv" >nul 2>nul
if errorlevel 1 (
    echo Installing the required libraries, please wait...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Installation failed. Check your internet connection and try again.
        pause
        exit /b 1
    )
)

echo Starting the bot...
python bot.py
echo.
echo The bot has stopped.
pause
