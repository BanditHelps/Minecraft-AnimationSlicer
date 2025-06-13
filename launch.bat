@echo off
title Minecraft Skin Animation Slicer
echo.
echo 🎮 Minecraft Skin Animation Slicer
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH!
    echo.
    echo 📥 Please install Python from: https://python.org
    echo    Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Launch the application
echo 🚀 Starting application...
python launch.py

pause 