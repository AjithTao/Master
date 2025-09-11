@echo off
echo 🚀 Leadership Quality Tool - Quick Setup
echo ======================================

echo.
echo 📋 Checking prerequisites...

:: Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git is not installed. Please install Git first.
    echo    Download from: https://git-scm.com/downloads
    pause
    exit /b 1
)
echo ✅ Git is installed

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python is installed

:: Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ first.
    echo    Download from: https://nodejs.org/
    pause
    exit /b 1
)
echo ✅ Node.js is installed

echo.
echo 🔧 Setting up backend...

:: Navigate to backend directory
cd backend

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

:: Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

:: Create config file if it doesn't exist
if not exist "config.env" (
    echo Creating configuration file...
    copy config.env.template config.env
    echo.
    echo ⚠️  IMPORTANT: Please edit backend\config.env and add your OpenAI API key
    echo    Get your API key from: https://platform.openai.com/api-keys
    echo.
)

echo.
echo 🎨 Setting up frontend...

:: Navigate to frontend directory
cd ..\frontend

:: Install Node.js dependencies
echo Installing Node.js dependencies...
npm install

echo.
echo ✅ Setup complete!
echo.
echo 🚀 To start the application:
echo    1. Run start.bat from the project root directory
echo    2. Or manually start backend and frontend
echo.
echo 📖 For detailed instructions, see TEAM_SETUP_GUIDE.md
echo.
echo 🌐 Application will be available at:
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:8000
echo.
pause
