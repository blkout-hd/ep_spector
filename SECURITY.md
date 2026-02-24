# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |
| < latest| :x:                |

## Reporting a Vulnerability

**DO NOT open public issues for security vulnerabilities.**

### Private Reporting Process

1. **GitHub Security Advisories** (Preferred)
   
   Report vulnerabilities privately via GitHub Security Advisories:
   https://github.com/[PRIVATE]/SPECTOR/security/advisories/new

2. **Email** (Alternative)
   
   If GitHub is not accessible, email security concerns to the repository owner.

### What to Include

When reporting a vulnerability, please provide:

- **Description**: Clear description of the vulnerability
- **Impact**: Potential impact if exploited
- **Reproduction**: Steps to reproduce the issue
- **Affected Files**: Specific files and line numbers
- **Suggested Fix**: If you have a remediation suggestion

### Response Timeline

- **Acknowledgment**: Within 72 hours
- **Initial Assessment**: Within 5 business days
- **Resolution Plan**: Within 10 business days
- **Fix Deployment**: Timeline depends on severity and complexity

### Severity Levels

We use CVSS 3.1 scoring for vulnerability assessment:

| Severity | CVSS Score | Response Time |
|----------|------------|---------------|
| Critical | 9.0-10.0   | 24 hours      |
| High     | 7.0-8.9    | 72 hours      |
| Medium   | 4.0-6.9    | 5 days        |
| Low      | 0.1-3.9    | 10 days       |

### Disclosure Policy

- We will coordinate with the reporter to ensure responsible disclosure
- Public disclosure will occur after a fix is available
- Credit will be given to the reporter (unless anonymity is requested)

### Security Best Practices for Contributors

1. **Never commit secrets**: Use environment variables or secret management
2. **Sign your commits**: Use GPG or SSH key signing
3. **Follow secure coding guidelines**: See our security documentation
4. **Report suspicious code**: Even in dependencies

### Security Scanning

This project employs automated security scanning:

- **Gitleaks**: Secret detection in git history
- **Detect-secrets**: Pre-commit secret scanning
- **TruffleHog**: Verified credential detection
- **Dependabot**: Vulnerable dependency monitoring
- **CodeQL**: Static analysis (planned)

### Security Headers

All web components implement:

- Content Security Policy (CSP)
- X-Frame-Options
- X-Content-Type-Options
- Strict-Transport-Security

---

**Last Updated**: 2026-02-19
**Contact**: @[PRIVATE] via GitHub Security Advisories
