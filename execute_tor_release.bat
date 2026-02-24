@echo off
REM SPECTOR OSS Release - Tor Integration
REM Automated Git commit and push

echo.
echo ======================================================================
echo     SPECTOR OSS RELEASE AUTOMATION - TOR INTEGRATION
echo ======================================================================
echo.

cd /d D:\DEV\SPECTOR
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Could not change to D:\DEV\SPECTOR
    pause
    exit /b 1
)

echo Current directory: %CD%
echo.

echo ======================================================================
echo Step 1: Check Git Status
echo ======================================================================
git status
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git status failed
    pause
    exit /b 1
)
echo.

echo ======================================================================
echo Step 2: Verify GitHub Remote
echo ======================================================================
git remote -v
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git remote check failed
    pause
    exit /b 1
)
echo.

echo ======================================================================
echo Step 3: Stage All Changes
echo ======================================================================
git add .
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git add failed
    pause
    exit /b 1
)
echo SUCCESS: All changes staged
echo.

echo ======================================================================
echo Step 4: Commit Changes
echo ======================================================================
git commit -m "feat: add Tor integration with Tornado automation" -m "" -m "- Add TorManager for automated Tor service lifecycle" -m "- Add Tornado web framework integration" -m "- Add real-time Tor dashboard with WebSocket" -m "- Add SOCKS proxy support for anonymous requests" -m "- Add circuit management and exit node control" -m "- Update dependencies (tornado, stem, PySocks)" -m "- Add tor-admin CLI command" -m "- Add comprehensive Tor integration guide" -m "" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git commit failed
    pause
    exit /b 1
)
echo SUCCESS: Changes committed
echo.

echo ======================================================================
echo Step 5: Push to GitHub (Private Repo)
echo ======================================================================
git push origin main
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git push failed
    pause
    exit /b 1
)
echo SUCCESS: Pushed to GitHub
echo.

echo.
echo ======================================================================
echo.
echo                 SUCCESS - OSS RELEASE COMPLETE!
echo.
echo   Tor integration added
echo   Tornado automation configured
echo   Dependencies updated
echo   Committed and pushed to GitHub
echo.
echo   Next Steps:
echo   1. Test: python launcher.py tor-admin
echo   2. Access: http://localhost:8889/tor/dashboard
echo   3. Review: TOR_INTEGRATION_GUIDE.md
echo.
echo ======================================================================
echo.

pause
