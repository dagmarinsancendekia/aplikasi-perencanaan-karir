@echo off
rem Pindah ke direktori tempat file batch ini berada
cd /d "%~dp0"
call venv\Scripts\activate
python app.py
pause