@echo off
title AI Employee - Gmail Watcher
echo ================================================
echo    AI Employee System - Gmail Watcher
echo ================================================
echo.
echo Starting email monitoring with Claude AI...
echo.
cd /d "%~dp0"
python gmail_watcher.py
pause
