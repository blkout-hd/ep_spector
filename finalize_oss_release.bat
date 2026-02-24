@echo off
REM SPECTOR OSS Release - Complete Finalization Script
REM This script completes the OSS release preparation

echo.
echo ================================================================
echo   SPECTOR OSS Release - Final Steps
echo ================================================================
echo.

cd /d "%~dp0"

REM Step 1: Run cleanup script
echo [1/3] Running cleanup script...
call cleanup_for_oss.bat
if errorlevel 1 (
    echo ERROR: Cleanup script failed
    exit /b 1
)

echo.
echo [2/3] Verifying changes...
echo.
echo Modified files:
git status --short
echo.

REM Step 2: Stage all changes
echo [3/3] Staging all changes...
git add .
if errorlevel 1 (
    echo ERROR: Git add failed
    exit /b 1
)

echo.
echo ================================================================
echo   All automated steps complete!
echo ================================================================
echo.
echo MANUAL STEPS REMAINING:
echo   1. Review staged changes: git status
echo   2. Commit: git commit -m "feat: prepare OSS release with Tornado admin console"
echo   3. Push: git push origin main
echo.
echo TO COMMIT AND PUSH NOW, run:
echo   git commit -m "feat: prepare OSS release with Tornado admin console" ^&^& git push origin main
echo.
pause
