@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "APP_TITLE=AutoMusic Planner"
set "GUI_FILE=%SCRIPT_DIR%automusic_scheduler_gui.pyw"

where py >nul 2>nul
if %errorlevel%==0 (
    start "" pyw "%GUI_FILE%"
    goto :eof
)

where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw "%GUI_FILE%"
    goto :eof
)

where python >nul 2>nul
if %errorlevel%==0 (
    start "" python "%GUI_FILE%"
    goto :eof
)

start "" "https://www.python.org/downloads/windows/"
powershell -NoProfile -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('Python is required before you can run AutoMusic Planner. Install Python from python.org, then start the program again.','AutoMusic Planner')" >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is required before you can run AutoMusic Planner.
    echo Install Python from: https://www.python.org/downloads/windows/
    pause
)
endlocal
