@echo off
REM Build script for Desktop Buddy Windows Executable
REM This creates a standalone .exe file that users can run

echo ================================
echo Desktop Buddy Build Script
echo ================================
echo.

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

echo.
echo Step 1: Installing PyInstaller...
pip install pyinstaller

echo.
echo Step 2: Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Step 3: Building executable...
echo This may take a few minutes...
pyinstaller DesktopBuddy.spec

echo.
echo Step 4: Checking build...
if exist dist\DesktopBuddy.exe (
    echo.
    echo ================================
    echo ✅ BUILD SUCCESSFUL!
    echo ================================
    echo.
    echo Executable created: dist\DesktopBuddy.exe
    echo Size: 
    dir dist\DesktopBuddy.exe | find "DesktopBuddy.exe"
    echo.
    echo To distribute:
    echo 1. Share the entire 'dist' folder
    echo 2. Or just DesktopBuddy.exe (users will need to add config)
    echo.
    echo To test: dist\DesktopBuddy.exe
    echo.
) else (
    echo.
    echo ================================
    echo ❌ BUILD FAILED
    echo ================================
    echo Check the error messages above
    echo.
)

pause
