#!/usr/bin/env python3
import sys
from pathlib import Path
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", default=[])
    args = parser.parse_args()
    
    REQUIRED = ["README.md", "ARCHITECTURE.md"]
    missing = []
    
    for f in args.files:
        if Path(f).name in REQUIRED:
            try:
                if "DISCLAIMER" not in Path(f).read_text(encoding="utf-8", errors="ignore"):
                    missing.append(f)
            except:
                pass
    
    if missing:
        print(f"⚠️  {len(missing)} file(s) missing DISCLAIMER.md reference")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
