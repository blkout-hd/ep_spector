# SPECTOR Security Quick Reference

## Pre-Commit Hooks

### Installation
```bash
pip install pre-commit
pre-commit install
```

### Run Manually
```bash
# All files
pre-commit run --all-files

# Specific hook
pre-commit run gitleaks --all-files
pre-commit run bandit --all-files

# Skip hooks (emergency only)
git commit --no-verify
```

### Update Hooks
```bash
pre-commit autoupdate
```

---

## Secret Detection

### Gitleaks
```bash
# Scan all history
gitleaks detect --source . --verbose

# Scan specific commit
gitleaks detect --log-opts="<commit-sha>"

# Scan uncommitted files
gitleaks protect --staged
```

### detect-secrets
```bash
# Scan all files
detect-secrets scan --baseline .secrets.baseline

# Audit findings
detect-secrets audit .secrets.baseline

# Update baseline
detect-secrets scan --update .secrets.baseline
```

### TruffleHog
```bash
# Scan filesystem
trufflehog filesystem --directory=. --only-verified

# Scan git history
trufflehog git file://. --only-verified --json
```

---

## PII Scanner

### Basic Scan
```bash
python scripts/pii_scanner.py src/ docs/ README.md
```

### Verbose Mode
```bash
python scripts/pii_scanner.py -v *.md *.py
```

### Allowlist Patterns
Edit `scripts/pii_scanner.py`:
```python
ALLOWLIST = [
    r"127\.0\.0\.1",
    r"example@example\.com",
    r"dev@SPECTOR\.corp",
]
```

---

## Code Security (Bandit)

### Scan Python Code
```bash
bandit -r src/ -f json -o bandit-report.json
```

### Scan with Confidence Filter
```bash
bandit -r src/ -ll  # Low confidence, Low severity
bandit -r src/ -lll # Medium confidence
```

### Ignore Specific Issues
```python
# nosec B101
password = input("Enter password: ")  # Safe in this context
```

---

## Dependency Scanning

### Safety (Python)
```bash
# Generate requirements
pip-compile pyproject.toml -o requirements.txt

# Scan
safety check -r requirements.txt --full-report

# Scan with ignore
safety check --ignore 12345
```

### npm audit (if Node.js used)
```bash
npm audit
npm audit fix
npm audit fix --force
```

---

## Docker Security

### Scan Images
```bash
# Trivy
trivy image spector-django:latest

# Grype
grype spector-django:latest
```

### Verify No Secrets in Images
```bash
docker history spector-django:latest --no-trunc | grep -i password
```

### Health Check Status
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

---

## Environment Variables

### Required Variables
All must be set in `.env`:
```bash
NEO4J_PASSWORD=
REDIS_PASSWORD=
MONGO_PASSWORD=
POSTGRES_PASSWORD=
QDRANT_API_KEY=
CHROMA_TOKEN=
DJANGO_SECRET_KEY=
```

### Generate Django Secret
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Verify No Defaults
```bash
grep -r "password.*=" docker-compose.yml | grep -v '${'
# Should return empty
```

---

## Audit Logging

### Log Format (NDJSON)
```json
{"timestamp":"2026-02-19T21:49:00Z","event_type":"access","user":"admin","action":"READ","resource":"/api/documents/123","status":"SUCCESS","ip":"127.0.0.1"}
```

### Validate Logs
```bash
python scripts/audit_log_check.py audit_logs/*.json
```

### Query Logs
```bash
# Failed auth attempts
jq 'select(.event_type=="auth" and .status=="FAILED")' audit.log

# Suspicious actions
jq 'select(.action | test("DELETE|PURGE|MODIFY"))' audit.log
```

---

## Forensic Sanitization

### Remove Secrets from History
```bash
# WARNING: Rewrites history!
bfg --replace-text passwords.txt
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### Verify Clean History
```bash
git log --all --full-history --source --grep="password\|secret\|token" -i
```

### Scrub File Completely
```bash
# Add to .gitignore first!
git filter-branch --index-filter 'git rm --cached --ignore-unmatch secrets.txt' HEAD
```

---

## Compliance Checks

### OWASP ASVS
```bash
# V14.3.1: Secret detection
pre-commit run gitleaks --all-files

# V9.1.1: Security logging
python scripts/audit_log_check.py audit_logs/

# V2.10.1: No hardcoded secrets
grep -r "password\s*=" src/ | grep -v '${' | grep -v '#'
```

### NIST SP 800-53
```bash
# IA-5: Authenticator management
grep -i "password" .env.example | grep "="
# Should show empty templates only

# SC-8: Transmission protection
grep -i "ssl\|tls" docker-compose.yml
```

### GDPR Article 32
```bash
# PII detection
python scripts/pii_scanner.py -v src/ docs/

# Data encryption verification
grep -i "encrypt" docker-compose.yml pyproject.toml
```

---

## Incident Response

### Secret Exposed
1. **Immediate:**
   ```bash
   # Rotate secret immediately
   # Add to .gitignore
   echo "leaked_secret.txt" >> .gitignore
   ```

2. **Clean History:**
   ```bash
   bfg --delete-files leaked_secret.txt
   git push --force
   ```

3. **Notify:**
   - Stakeholders
   - Service providers (revoke API keys)
   - Users (if PII exposed)

### PII Exposure
1. **Document:**
   ```bash
   python scripts/pii_scanner.py > pii_findings.txt
   ```

2. **Remediate:**
   - Remove PII from code
   - Update with placeholders
   - Add to PII scanner allowlist if needed

3. **Notify:**
   - Data Protection Officer (if EU)
   - Affected individuals (within 72 hours, GDPR)

### Vulnerability Disclosure
1. **Assess Severity:** CVSS 3.1 calculator
2. **Private Report:** GitHub Security Advisories
3. **Patch:** Create fix in private fork
4. **Coordinate:** 90-day disclosure timeline
5. **Publish:** CVE assignment, patch release

---

## CI/CD Integration

### GitHub Actions
```yaml
name: Security Scan
on: [push, pull_request]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - name: Install dependencies
        run: pip install pre-commit bandit safety
      - name: Run pre-commit
        run: pre-commit run --all-files
      - name: Run Bandit
        run: bandit -r src/ -f json -o bandit.json
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: bandit.json
```

---

## Emergency Contacts

| Incident Type | Contact | SLA |
|---------------|---------|-----|
| Secret Exposure | security@SPECTOR.corp | 1 hour |
| PII Breach | dpo@SPECTOR.corp | 24 hours |
| Vulnerability Report | GitHub Security Advisory | 72 hours |
| Service Outage | ops@SPECTOR.corp | 15 minutes |

---

## Useful Commands

### Check Pre-commit Status
```bash
pre-commit run --all-files --verbose
```

### Verify Docker Security
```bash
docker inspect spector-neo4j | jq '.[0].HostConfig.Privileged'
# Should return: false
```

### List Exposed Ports
```bash
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep "0.0.0.0"
# Should return empty (all 127.0.0.1)
```

### Generate SBOM
```bash
# Python
pip install pip-sbom
pip-sbom > sbom.json

# Syft (all languages)
syft scan . -o json > sbom.spdx.json
```

---

**Last Updated:** 2026-02-19  
**Owner:** SPECTOR Contributors Security Team  
**Version:** 1.0.0
