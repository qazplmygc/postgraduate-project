# EdgeNexus deploy -> Gitee (fast in China, no VPN)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Set-Location $PSScriptRoot

$GITEE_USER = "qazplmygc"
$GITEE_REPO = "postgraduate-project"
$GITHUB_URL = "https://github.com/qazplmygc/postgraduate-project"
$GITEE_URL = "https://gitee.com/$GITEE_USER/$GITEE_REPO"
$PAGES_URL = "https://$GITEE_USER.gitee.io/$GITEE_REPO/"

Write-Host ""
Write-Host "EdgeNexus -> Gitee (China, no VPN)" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# --- Method A: push with token ---
if ($env:GITEE_TOKEN) {
    Write-Host "[token] pushing to Gitee ..." -ForegroundColor Yellow
    git remote remove gitee 2>$null
    git remote add gitee "https://oauth2:$($env:GITEE_TOKEN)@gitee.com/$GITEE_USER/$GITEE_REPO.git"
    git push -u gitee main --force
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "Push OK!" -ForegroundColor Green
        Write-Host "Enable Pages: $GITEE_URL -> Services -> Gitee Pages -> Deploy branch main -> Update" -ForegroundColor White
        Write-Host "Site URL: $PAGES_URL" -ForegroundColor Cyan
        Read-Host "Press Enter"
        exit 0
    }
}

# --- Method B: import from GitHub (no token, one-time in browser) ---
Write-Host "No GITEE_TOKEN found. Use Gitee 'Import from GitHub' (easiest):" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Browser opens Gitee import page" -ForegroundColor White
Write-Host "  2. Paste GitHub URL: $GITHUB_URL" -ForegroundColor White
Write-Host "  3. Import -> open repo -> Services -> Gitee Pages -> branch main -> Start/Update" -ForegroundColor White
Write-Host "  4. Your URL: $PAGES_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "Optional: set token for auto push next time:" -ForegroundColor DarkGray
Write-Host '  Gitee -> Settings -> Private Token -> set env: $env:GITEE_TOKEN="xxx"' -ForegroundColor DarkGray
Write-Host ""

$open = Read-Host "Open Gitee import page now? [Y/n]"
if ($open -ne 'n' -and $open -ne 'N') {
    Start-Process "https://gitee.com/projects/import/github"
}

Read-Host "Press Enter to exit"
