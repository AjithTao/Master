@echo off
REM Leadership Quality Tool - Root Launcher Script
REM This script calls the actual startup script from the scripts folder

echo 🚀 Starting Leadership Quality Tool...
echo ==================================

REM Check if scripts folder exists
if not exist "scripts" (
    echo ❌ Error: Scripts folder not found
    echo Please ensure you're running this from the project root directory
    pause
    exit /b 1
)

REM Check if start.bat exists in scripts folder
if not exist "scripts\start.bat" (
    echo ❌ Error: start.bat not found in scripts folder
    pause
    exit /b 1
)

echo 📁 Found startup script in scripts folder
echo 🔄 Launching application...

REM Call the actual startup script
call scripts\start.bat

REM If we get here, the script finished
pause
