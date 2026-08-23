@echo off
setlocal
set "ROOT=%~dp0"
set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"
if not exist "%ROOT%.venv\Scripts\python.exe" (
  py -3 "%ROOT%setup_environment.py" || python "%ROOT%setup_environment.py" || exit /b 1
)
"%ROOT%.venv\Scripts\python.exe" "%ROOT%worthir.py" %*
