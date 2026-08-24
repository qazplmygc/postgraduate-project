@echo off
chcp 65001 >nul
cd /d "%~dp0"
start "" "https://gitee.com/projects/import/github"
echo.
echo  ====================================================
echo   Gitee 国内站开通（3 步，只需做一次）
echo  ====================================================
echo.
echo  1. 浏览器已打开 Gitee 导入页
echo  2. 粘贴 GitHub 地址：
echo     https://github.com/qazplmygc/postgraduate-project
echo  3. 导入完成后 -^> 服务 -^> Gitee Pages -^> 分支 main -^> 启动
echo.
echo  最终地址（正常网页，不是代码）：
echo  https://qazplmygc.gitee.io/postgraduate-project/search/index.html
echo.
pause
