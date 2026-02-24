# SPECTOR Security Remediation - History Purge Script
# CRITICAL: Execute this BEFORE pushing any other changes
# This script removes sensitive data from entire git history

Write-Host "========================================" -ForegroundColor Red
Write-Host "SPECTOR HISTORY PURGE - CRITICAL STEP" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""
Write-Host "This script will:" -ForegroundColor Yellow
Write-Host "  1. Remove Windows path (C:\Users\blkout) from ALL history" -ForegroundColor Yellow
Write-Host "  2. Remove memory.json from entire git history" -ForegroundColor Yellow
Write-Host "  3. Remove .qwen/ directory from entire git history" -ForegroundColor Yellow
Write-Host "  4. Force push all branches (COORDINATE WITH COLLABORATORS)" -ForegroundColor Yellow
Write-Host ""
Write-Host "WARNING: This is DESTRUCTIVE and IRREVERSIBLE" -ForegroundColor Red
Write-Host "All collaborators must re-clone after this operation" -ForegroundColor Red
Write-Host ""

$confirm = Read-Host "Type 'PURGE' to confirm you understand the consequences"
if ($confirm -ne "PURGE") {
    Write-Host "Aborted. No changes made." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 1: Installing git-filter-repo..." -ForegroundColor Cyan
pip install git-filter-repo
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install git-filter-repo. Please install manually:" -ForegroundColor Red
    Write-Host "  pip install git-filter-repo" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Step 2: Creating replacement file for Windows paths..." -ForegroundColor Cyan
$replaceText = "C:\Users\blkout==>REDACTED_PATH"
$replaceText | Out-File -FilePath "replacement-map.txt" -Encoding ASCII
Write-Host "  Created replacement-map.txt" -ForegroundColor Green

Write-Host ""
Write-Host "Step 3: Purging Windows path from ALL history..." -ForegroundColor Cyan
Write-Host "  This may take several minutes..." -ForegroundColor Yellow
git filter-repo --replace-text replacement-map.txt --force
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to purge Windows paths" -ForegroundColor Red
    exit 1
}
Write-Host "  Windows paths removed from history" -ForegroundColor Green

Write-Host ""
Write-Host "Step 4: Removing memory.json from entire history..." -ForegroundColor Cyan
git filter-repo --path memory.json --invert-paths --force
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to remove memory.json" -ForegroundColor Red
    exit 1
}
Write-Host "  memory.json removed from history" -ForegroundColor Green

Write-Host ""
Write-Host "Step 5: Removing .qwen/ directory from entire history..." -ForegroundColor Cyan
git filter-repo --path .qwen --invert-paths --force
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to remove .qwen/ directory" -ForegroundColor Red
    exit 1
}
Write-Host "  .qwen/ directory removed from history" -ForegroundColor Green

Write-Host ""
Write-Host "Step 6: Cleaning up temporary files..." -ForegroundColor Cyan
Remove-Item -Path "replacement-map.txt" -Force
Write-Host "  Temporary files removed" -ForegroundColor Green

Write-Host ""
Write-Host "Step 7: Verifying cleanup..." -ForegroundColor Cyan
$windowsPaths = git log --all -p | Select-String "C:\\Users\\blkout" -SimpleMatch
if ($windowsPaths) {
    Write-Host "  WARNING: Some Windows paths may still exist in history" -ForegroundColor Yellow
} else {
    Write-Host "  No Windows paths found in history" -ForegroundColor Green
}

$memoryJson = git log --all --name-only | Select-String "memory.json" -SimpleMatch
if ($memoryJson) {
    Write-Host "  WARNING: memory.json references may still exist" -ForegroundColor Yellow
} else {
    Write-Host "  No memory.json references found" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "HISTORY PURGE COMPLETED SUCCESSFULLY" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS (MANUAL):" -ForegroundColor Yellow
Write-Host "  1. Review changes: git log --oneline" -ForegroundColor White
Write-Host "  2. Force push to origin (COORDINATE FIRST):" -ForegroundColor White
Write-Host "     git push origin --force --all" -ForegroundColor White
Write-Host "     git push origin --force --tags" -ForegroundColor White
Write-Host "  3. Notify all collaborators to re-clone" -ForegroundColor White
Write-Host ""
Write-Host "IMPORTANT: All collaborators must:" -ForegroundColor Red
Write-Host "  - Delete their local clone" -ForegroundColor Red
Write-Host "  - Re-clone from the remote" -ForegroundColor Red
Write-Host "  - NOT attempt to merge old history" -ForegroundColor Red
Write-Host ""
