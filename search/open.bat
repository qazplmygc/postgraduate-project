@echo off
chcp 65001 >nul
cd /d "%~dp0"

powershell -NoProfile -Command "try { $c = New-Object Net.Sockets.TcpClient('127.0.0.1',8765); $c.Close(); exit 0 } catch { exit 1 }" >nul 2>&1
if errorlevel 1 (
  start "EdgeNexus Server" /MIN python "%~dp0server.py"
)

set /a _n=0
:wait_ready
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8765/api/health' -UseBasicParsing -TimeoutSec 2; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if not errorlevel 1 goto ready
set /a _n+=1
if %_n% GEQ 20 (
  echo Server start timed out. Install Python and run: python server.py
  pause
  exit /b 1
)
timeout /t 1 /nobreak >nul
goto wait_ready

:ready
start "" "http://127.0.0.1:8765/search/index.html"
echo EdgeNexus started.
echo Search:    http://127.0.0.1:8765/search/index.html
echo Patents:   http://127.0.0.1:8765/patents/index.html
echo Reproduce: http://127.0.0.1:8765/reproduce/index.html
echo Videos:    http://127.0.0.1:8765/videos/index.html
echo Close the "EdgeNexus Server" window to stop.
