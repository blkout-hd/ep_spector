@echo off
REM SPECTOR Open Source Release - Cleanup Script
REM This script removes enterprise-specific files and prepares for OSS release

echo.
echo ================================================================
echo   SPECTOR - Open Source Release Cleanup
echo ================================================================
echo.

cd /d "%~dp0"

REM Step 1: Remove artifacts
echo [1/5] Removing database and log artifacts...
if exist "enhanced_gpt_offloader_v4.db" del /F /Q "enhanced_gpt_offloader_v4.db" && echo   - Removed: enhanced_gpt_offloader_v4.db
if exist "ai_ants_nexus_agi.log" del /F /Q "ai_ants_nexus_agi.log" && echo   - Removed: ai_ants_nexus_agi.log
if exist "memory.json" del /F /Q "memory.json" && echo   - Removed: memory.json
if exist ".mailmap" del /F /Q ".mailmap" && echo   - Removed: .mailmap

REM Step 2: Remove enterprise internal docs
echo.
echo [2/5] Removing enterprise internal documentation...
if exist "SECURITY_AUDIT_REMEDIATION_FINAL_REPORT.md" del /F /Q "SECURITY_AUDIT_REMEDIATION_FINAL_REPORT.md"
if exist "SECURITY_IMPLEMENTATION_COMPLETE.md" del /F /Q "SECURITY_IMPLEMENTATION_COMPLETE.md"
if exist "SECURITY_REMEDIATION_COMPLETE.md" del /F /Q "SECURITY_REMEDIATION_COMPLETE.md"
if exist "SECURITY_REMEDIATION_EXECUTION_PLAN.md" del /F /Q "SECURITY_REMEDIATION_EXECUTION_PLAN.md"
if exist "REPOSITORY_STATUS_CLEAN_SLATE.md" del /F /Q "REPOSITORY_STATUS_CLEAN_SLATE.md"
if exist "HISTORY_PURGE_QUICK_REFERENCE.md" del /F /Q "HISTORY_PURGE_QUICK_REFERENCE.md"
if exist "docs\LEGAL_RISK_ASSESSMENT.md" del /F /Q "docs\LEGAL_RISK_ASSESSMENT.md"
if exist "docs\LEGAL_COMPLIANCE_IMPLEMENTATION.md" del /F /Q "docs\LEGAL_COMPLIANCE_IMPLEMENTATION.md"
if exist "docs\LEGAL_RISK_EXECUTIVE_SUMMARY.md" del /F /Q "docs\LEGAL_RISK_EXECUTIVE_SUMMARY.md"
if exist "docs\LEGAL_COMPLIANCE_QUICK_REFERENCE.md" del /F /Q "docs\LEGAL_COMPLIANCE_QUICK_REFERENCE.md"
echo   - Removed 10 enterprise documents

REM Step 3: Backup old files
echo.
echo [3/5] Backing up old files...
if exist "README.md" (
    if not exist "README_OLD.md" move /Y "README.md" "README_OLD.md" >nul
    echo   - Backed up: README.md -^> README_OLD.md
)
if exist "DISCLAIMER.md" (
    if not exist "DISCLAIMER_OLD.md" move /Y "DISCLAIMER.md" "DISCLAIMER_OLD.md" >nul
    echo   - Backed up: DISCLAIMER.md -^> DISCLAIMER_OLD.md
)

REM Step 4: Install OSS versions
echo.
echo [4/5] Installing OSS-friendly files...
if exist "README_OSS.md" (
    copy /Y "README_OSS.md" "README.md" >nul
    echo   - Installed: README.md (OSS version)
)
if exist "DISCLAIMER_OSS.md" (
    copy /Y "DISCLAIMER_OSS.md" "DISCLAIMER.md" >nul
    echo   - Installed: DISCLAIMER.md (OSS version)
)

REM Keep LICENSE-MIT and LICENSE-AGPL, but create main LICENSE pointing to MIT
if exist "LICENSE-MIT" (
    copy /Y "LICENSE-MIT" "LICENSE" >nul
    echo   - Installed: LICENSE (MIT)
)

REM Step 5: Clean up duplicate licenses (optional - keep split license for now)
REM if exist "LICENSE-AGPL" del /F /Q "LICENSE-AGPL"

echo.
echo [5/5] Final verification...

REM Count remaining files
echo.
echo Artifact status:
if not exist "enhanced_gpt_offloader_v4.db" (echo   [OK] No .db files) else (echo   [WARN] .db files still present)
if not exist "ai_ants_nexus_agi.log" (echo   [OK] No .log files) else (echo   [WARN] .log files still present)
if not exist "memory.json" (echo   [OK] No runtime state files) else (echo   [WARN] Runtime state files still present)
if not exist ".mailmap" (echo   [OK] No PII metadata files) else (echo   [WARN] PII metadata files still present)

echo.
echo ================================================================
echo   Cleanup Complete!
echo ================================================================
echo.
echo NEXT STEPS:
echo   1. Review OSS_RELEASE_SUMMARY.md for manual metadata updates
echo   2. Edit pyproject.toml to update author (SPECTOR Contributors -^> SPECTOR Contributors)
echo   3. Edit scripts/pii_scanner.py to update email allowlist
echo   4. Run: pre-commit run --all-files
echo   5. Run: python scripts/pii_scanner.py --all
echo   6. Review git status and commit changes
echo.
pause
