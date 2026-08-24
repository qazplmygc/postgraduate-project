# EdgeNexus deploy to GitHub Pages (UTF-8 safe)
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Set-Location $PSScriptRoot

Write-Host ""
Write-Host "EdgeNexus -> GitHub Pages" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: git not found. Install Git: https://git-scm.com/download/win" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path ".git")) {
    Write-Host "[1/5] git init ..." -ForegroundColor Yellow
    git init -b main
    git add -A
    git commit -m "EdgeNexus: cloud-edge research site"
} else {
    Write-Host "[1/5] git repo OK" -ForegroundColor Green
}

$hasOrigin = $false
try {
    $null = git remote get-url origin 2>$null
    if ($LASTEXITCODE -eq 0) { $hasOrigin = $true }
} catch {}

if (-not $hasOrigin) {
    Write-Host ""
    Write-Host "Create a PUBLIC repo on GitHub first: https://github.com/new" -ForegroundColor White
    Write-Host "Repo name suggestion: edgenexus" -ForegroundColor White
    Write-Host ""
    $ghUser = Read-Host "Your GitHub username"
    if ([string]::IsNullOrWhiteSpace($ghUser)) {
        Write-Host "Cancelled: no username." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    $repo = Read-Host "Repo name [edgenexus]"
    if ([string]::IsNullOrWhiteSpace($repo)) { $repo = "edgenexus" }
    $url = "https://github.com/$ghUser/$repo.git"
    Write-Host "[2/5] git remote add origin $url" -ForegroundColor Yellow
    git remote add origin $url
} else {
    Write-Host "[2/5] remote origin OK: $(git remote get-url origin)" -ForegroundColor Green
}

Write-Host "[3/5] git add ..." -ForegroundColor Yellow
git add -A
git status --short

$msg = Read-Host "Commit message [update]"
if ([string]::IsNullOrWhiteSpace($msg)) { $msg = "update" }

Write-Host "[4/5] git commit ..." -ForegroundColor Yellow
git commit -m $msg 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "(nothing new to commit, continuing push...)" -ForegroundColor DarkGray
}

Write-Host "[5/5] git push ..." -ForegroundColor Yellow
Write-Host "If browser opens, sign in to GitHub." -ForegroundColor DarkGray
git push -u origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "PUSH FAILED. Common fixes:" -ForegroundColor Red
    Write-Host "  1. Create the empty repo on GitHub first (same name)" -ForegroundColor White
    Write-Host "  2. Run: gh auth login   OR use Git Credential Manager" -ForegroundColor White
    Write-Host "  3. Manual push:" -ForegroundColor White
    Write-Host "     git push -u origin main" -ForegroundColor Gray
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "SUCCESS!" -ForegroundColor Green
Write-Host "Enable Pages: repo -> Settings -> Pages -> Source: GitHub Actions" -ForegroundColor White
Write-Host "Wait 1-2 min, then open:" -ForegroundColor White
$origin = (git remote get-url origin) -replace '\.git$',''
$pages = $origin -replace 'github\.com','github.io'
Write-Host "  $pages/" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"
