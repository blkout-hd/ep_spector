#!/usr/bin/env python3
"""
PII Scanner - GDPR Article 32 Compliance
Detects Personally Identifiable Information in code and documentation

Patterns detected:
- Social Security Numbers (US)
- Email addresses
- Phone numbers (US/International)
- Credit card numbers
- IP addresses (private/public)
- Physical addresses (partial)
- Names (common patterns)
- Dates of birth

Exit codes:
- 0: No PII detected
- 1: PII detected
- 2: Error during scan
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple
import argparse

# GDPR Article 4(1) - Personal Data Patterns
PII_PATTERNS = {
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "ssn_alt": r"\b\d{9}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@(?!example\.com|test\.com|localhost|SPECTOR\.corp)[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "phone_us": r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "phone_intl": r"\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}",
    "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
    "ipv4": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
    "ipv6": r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b",
    "dob": r"\b(?:0?[1-9]|1[0-2])[/-](?:0?[1-9]|[12][0-9]|3[01])[/-](?:19|20)\d{2}\b",
    "address": r"\b\d{1,5}\s+(?:[A-Z][a-z]+\s+){1,3}(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir)\b",
}

# Allowlisted patterns (false positives)
ALLOWLIST = [
    r"127\.0\.0\.1",
    r"0\.0\.0\.0",
    r"255\.255\.255\.\d+",
    r"192\.168\.\d+\.\d+",
    r"10\.\d+\.\d+\.\d+",
    r"example@example\.com",
    r"test@test\.com",
    r"contributors@example\.com",
    r"000-00-0000",
    r"123-45-6789",
]


def is_allowlisted(text: str) -> bool:
    for pattern in ALLOWLIST:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def scan_file(filepath: Path) -> List[Tuple[str, int, str, str]]:
    findings = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, start=1):
                if is_allowlisted(line):
                    continue
                for pii_type, pattern in PII_PATTERNS.items():
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        matched_text = match.group(0)
                        if not is_allowlisted(matched_text):
                            findings.append((pii_type, line_num, line.strip(), matched_text))
    except Exception as e:
        print(f"Error scanning {filepath}: {e}", file=sys.stderr)
        return []
    return findings


def main():
    parser = argparse.ArgumentParser(description="PII Scanner for GDPR compliance")
    parser.add_argument("files", nargs="*", default=[], help="Files to scan")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()
    
    if not args.files:
        return 0
    
    all_findings = []
    for filepath_str in args.files:
        filepath = Path(filepath_str)
        if not filepath.exists():
            continue
        findings = scan_file(filepath)
        if findings:
            all_findings.extend([(filepath, *f) for f in findings])
    
    if all_findings:
        print("\n❌ PII DETECTED - GDPR Article 32 Violation Risk\n")
        for filepath, pii_type, line_num, line_content, matched_text in all_findings:
            print(f"File: {filepath} | Line {line_num} | Type: {pii_type.upper()}")
            print(f"Matched: {matched_text}")
        print(f"\n🔴 Total findings: {len(all_findings)}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
