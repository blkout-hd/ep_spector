@echo off
REM SPECTOR OSS Release - Complete Automation Script
REM This script performs ALL steps including git push

echo.
echo ================================================================
echo   SPECTOR OSS Release - Complete Automation
echo ================================================================
echo.

cd /d "%~dp0"

REM Step 1: Run cleanup script
echo [1/5] Running cleanup script...
call cleanup_for_oss.bat
if errorlevel 1 (
    echo ERROR: Cleanup script failed
    pause
    exit /b 1
)

REM Step 2: Check git status
echo.
echo [2/5] Checking git status...
git --no-pager status

REM Step 3: Get GitHub remote URL
echo.
echo [3/5] GitHub remote URL:
git remote get-url origin

REM Step 4: Stage all changes
echo.
echo [4/5] Staging all changes...
git add .
if errorlevel 1 (
    echo ERROR: Git add failed
    pause
    exit /b 1
)

echo.
echo Staged files:
git --no-pager status --short

REM Step 5: Commit and push
echo.
echo [5/5] Committing and pushing changes...
git commit -m "feat: prepare OSS release with Tornado admin console" -m "" -m "- Updated metadata (contributors email)" -m "- Added Tornado admin console with web UI" -m "- Created admin dashboard and login templates" -m "- Added CLI command for admin console" -m "- Updated README with admin console documentation" -m "" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

if errorlevel 1 (
    echo ERROR: Git commit failed
    pause
    exit /b 1
)

echo.
echo Pushing to origin main...
git push origin main

if errorlevel 1 (
    echo ERROR: Git push failed
    pause
    exit /b 1
)

echo.
echo ================================================================
echo   SUCCESS! OSS Release Complete
echo ================================================================
echo.
echo Next steps:
echo   1. Verify changes on GitHub
echo   2. Test admin console: python launcher.py admin
echo   3. Review OSS_RELEASE_FINAL_STATUS.md for details
echo.
echo Admin Console Access:
echo   URL: http://localhost:8888
echo   Username: admin
echo   Password: spector
echo.
pause
