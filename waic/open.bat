@echo off
chcp 65001 >nul
cd /d "%~dp0..\search"
call open.bat
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8765/waic/index.html"
