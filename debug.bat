@echo off
echo ========================================
echo   Backend Jira Debug Tool
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if backend server is running
echo Checking if backend server is running...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo Warning: Backend server doesn't appear to be running
    echo Please start the backend server first:
    echo   cd backend
    echo   python main.py
    echo.
    echo Press any key to continue anyway...
    pause >nul
)

echo.
echo Choose debug option:
echo 1. Quick test (recommended)
echo 2. Comprehensive test
echo 3. Test specific question
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Running quick test...
    python debug_simple.py
) else if "%choice%"=="2" (
    echo.
    echo Running comprehensive test...
    python debug_backend_jira.py
) else if "%choice%"=="3" (
    echo.
    set /p question="Enter your question: "
    echo.
    echo Testing question: "%question%"
    python debug_simple.py "%question%"
) else if "%choice%"=="4" (
    echo Goodbye!
    exit /b 0
) else (
    echo Invalid choice. Please run the script again.
)

echo.
echo Debug test completed!
pause
