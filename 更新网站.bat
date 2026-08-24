@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo  EdgeNexus 自动更新网站（无需 Gitee 登录）
echo  ==========================================
echo.
git add -A
git status --short
echo.
git commit -m "update site" 2>nul
if errorlevel 1 echo (没有新改动，跳过提交)
git push origin main
if errorlevel 1 (
  echo.
  echo  推送失败。请确认网络可访问 GitHub。
  pause
  exit /b 1
)
echo.
echo  更新成功！约 1 分钟后生效。
echo.
echo  【唯一入口 · 无需登录 · 手机电脑都能开】
echo  https://qazplmygc.github.io/postgraduate-project/start.html
echo.
start "" "https://qazplmygc.github.io/postgraduate-project/start.html"
pause
