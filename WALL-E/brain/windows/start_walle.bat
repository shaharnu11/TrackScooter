@echo off
rem WALL-E talking, Windows (XPS). Double-click, or run from any folder.
rem Extra options pass through, e.g.:  start_walle.bat --mind cloud
cd /d "%~dp0.."
rem An old brain left running holds port 8089: stop it first.
taskkill /im llama-server.exe /f >nul 2>&1
if not exist ".venv\Scripts\python.exe" (
  echo No .venv here. Do the setup in windows\README.md first.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" talk.py --brain 4b-vl %*
pause
