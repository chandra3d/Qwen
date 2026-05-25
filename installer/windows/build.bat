@echo off
REM Blender AI Copilot Windows Build Script
REM Prerequisites: Node.js, Rust, Python 3.10+, Inno Setup

echo ========================================
echo Blender AI Copilot - Windows Build
echo ========================================
echo.

REM Check prerequisites
echo [1/7] Checking prerequisites...

REM Check Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)
echo ✓ Node.js installed

REM Check Rust
where cargo >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Rust not found. Please install Rust from rustup.rs
    pause
    exit /b 1
)
echo ✓ Rust installed

REM Check Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found. Please install Python 3.10+
    pause
    exit /b 1
)
echo ✓ Python installed

echo.
echo [2/7] Installing Python dependencies...
cd /d "%~dp0..\.."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [3/7] Building Desktop Client (Tauri)...
cd src\desktop_client
call npm install
call npm run tauri build

if not exist "src-tauri\target\release\blender-copilot.exe" (
    echo ERROR: Tauri build failed
    pause
    exit /b 1
)
echo ✓ Tauri build completed

echo.
echo [4/7] Preparing installer files...
cd ..\..\installer\windows

REM Create output directory
if not exist "output" mkdir output

REM Copy Python embedded distribution (download if needed)
if not exist "python-embed" (
    echo Downloading Python embedded distribution...
    REM User should download from python.org and extract here
    echo Please download Python embedded package from python.org
    echo and extract to installer\windows\python-embed
    pause
)

echo.
echo [5/7] Building Windows Installer...
where iscc >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Inno Setup Compiler not found. Skipping installer build.
    echo Download and install Inno Setup from jrsoftware.org
    goto :skip_installer
)

iscc setup.iss
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Installer build failed
    pause
    exit /b 1
)
echo ✓ Installer created successfully

:skip_installer
echo.
echo [6/7] Creating portable distribution...
cd ..\..\..
if exist "dist" rmdir /s /q dist
mkdir dist\BlenderAICopilot
xcopy /E /I src\desktop_client\src-tauri\target\release dist\BlenderAICopilot
xcopy /E /I src\backend dist\BlenderAICopilot\backend
xcopy /E /I src\memory_db dist\BlenderAICopilot\memory_db
xcopy /E /I src\ocr_service dist\BlenderAICopilot\ocr_service
xcopy /E /I src\blender_addon dist\BlenderAICopilot\blender_addon
copy requirements.txt dist\BlenderAICopilot
copy README.md dist\BlenderAICopilot
copy LICENSE dist\BlenderAICopilot
echo ✓ Portable distribution created

echo.
echo [7/7] Build Summary
echo ========================================
echo.
if exist "installer\windows\output\*.exe" (
    echo Installer: installer\windows\output\BlenderAICopilot-Setup-0.1.0.exe
) else (
    echo Installer: Not built (Inno Setup not installed)
)
echo Portable: dist\BlenderAICopilot\
echo.
echo Build completed!
echo.
echo Next steps:
echo 1. Test the application in dist\BlenderAICopilot\
echo 2. Install Blender add-on via Edit ^> Preferences ^> Add-ons
echo 3. Run blender-copilot.exe to start the AI assistant
echo.

pause
