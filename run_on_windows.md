
initially i did
```bash
cd mukta\mukta-main

py --version

python -m pip --version

python -m venv .venv

.venv\Scripts\activate

python -m pip install --upgrade pip

python -m pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib PyMuPDF PyQt6 pyqtdarktheme

python -m pip uninstall pyqtdarktheme -y

python -m pip install PyQtDarkTheme2

python -c "import qdarktheme; print(qdarktheme.__file__); print(hasattr(qdarktheme, 'setup_theme'))"
# should return true above

python main.py

python -m pip install pyinstaller

python -m PyInstaller --clean --windowed --name Mukta main.py

# to run
dist\Mukta\Mukta.exe
```
Use bat file 
```bash

@echo off
title Mukta Launcher
cd /d "%~dp0"

echo.
echo =================================
echo          MUKTA LAUNCHER
echo =================================
echo.
echo 1. Run using Python virtual environment
echo 2. Run using Python virtual environment (Debug)
echo 3. Run packaged EXE
echo 4. Exit
echo.

set /p choice="Select an option: "

if "%choice%"=="1" goto venv
if "%choice%"=="2" goto debug
if "%choice%"=="3" goto exe
if "%choice%"=="4" exit

echo Invalid option.
pause
exit

:venv
if not exist ".venv\Scripts\pythonw.exe" (
    echo Virtual environment not found.
    pause
    exit /b 1
)
start "" ".venv\Scripts\pythonw.exe" "main.py"
exit

:debug
if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" "main.py"
pause
exit

:exe
if not exist "dist\Mukta\Mukta.exe" (
    echo Packaged EXE not found.
    pause
    exit /b 1
)
start "" /D "%~dp0dist\Mukta" "%~dp0dist\Mukta\Mukta.exe"
exit

```
or add run_mukta.vbs
```bash
Set shell = CreateObject("WScript.Shell")

projectPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

shell.CurrentDirectory = projectPath

shell.Run """" & projectPath & "\.venv\Scripts\pythonw.exe"" """ & projectPath & "\main.py""", 0, False
```
