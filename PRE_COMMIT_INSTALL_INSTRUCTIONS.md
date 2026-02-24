# Pre-commit Installation Instructions

## Quick Installation

Run this command in your terminal:

```powershell
C:\Users\[USER]\AppData\Local\Programs\Python\Python314\python.exe -m pip install pre-commit
```

Or if you have Python in your PATH:

```powershell
python -m pip install pre-commit
```

## After Installation

Once pre-commit is installed, run:

```powershell
cd D:\DEV\SPECTOR
pre-commit install
```

You should see:
```
pre-commit installed at .git/hooks/pre-commit
```

## Verify Installation

```powershell
pre-commit --version
```

## Test It

Run a test to make sure everything works:

```powershell
pre-commit run --all-files
```

This will run all the security and quality checks on your entire codebase.

## What It Does

Once installed, pre-commit will automatically run these checks before every commit:

- **Gitleaks**: Detect secrets in code
- **detect-secrets**: Credential scanning
- **Black**: Python code formatting
- **Ruff**: Python linting and formatting
- **YAML/JSON/TOML validation**: Config file syntax
- **Merge conflict detection**: Catch conflict markers
- **Trailing whitespace cleanup**: Remove extra spaces
- **End-of-file fixer**: Ensure files end with newline
- **Large file detection**: Warn about files > 500KB
- **Private key detection**: Prevent key commits
- **Markdown linting**: Documentation quality
- **Julia formatting**: Julia code style
- **Windows path blocker**: Prevent path leakage
- **Password pattern blocker**: Catch hardcoded passwords

## If Installation Fails

Try these alternatives:

### Method 1: Upgrade pip first
```powershell
python -m pip install --upgrade pip
python -m pip install pre-commit
```

### Method 2: Use user install
```powershell
python -m pip install --user pre-commit
```

### Method 3: Use uv (if available)
```powershell
uv pip install pre-commit
```

## Manual Hook Installation (if needed)

If `pre-commit install` doesn't work, manually copy the hook:

```powershell
# The hook is at:
C:\Users\[USER]\AppData\Local\Programs\Python\Python314\Scripts\pre-commit.exe

# Copy to git hooks directory:
Copy-Item "C:\Users\[USER]\AppData\Local\Programs\Python\Python314\Scripts\pre-commit.exe" ".git\hooks\pre-commit"
```

## Uninstall

To remove pre-commit:

```powershell
pre-commit uninstall
pip uninstall pre-commit
```

---

**Note:** The installation is timing out due to network issues. Try running the commands manually when you have a stable connection.
