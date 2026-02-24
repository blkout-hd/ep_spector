# SPECTOR Pre-commit Hook Installation
Write-Host "Installing pre-commit..." -ForegroundColor Cyan

# Install pre-commit
& "C:\Users\blkout\AppData\Local\Programs\Python\Python314\python.exe" -m pip install pre-commit

# Verify installation
Write-Host "Verifying installation..." -ForegroundColor Green
& "C:\Users\blkout\AppData\Local\Programs\Python\Python314\python.exe" -m pre_commit --version

# Install git hooks
Write-Host "Installing git hooks..." -ForegroundColor Yellow
Set-Location D:\DEV\SPECTOR
& "C:\Users\blkout\AppData\Local\Programs\Python\Python314\python.exe" -m pre_commit install

Write-Host "Done! Pre-commit hooks are active." -ForegroundColor Green
