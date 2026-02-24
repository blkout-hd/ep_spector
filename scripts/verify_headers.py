#!/usr/bin/env python3
import sys
from pathlib import Path
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", default=[])
    args = parser.parse_args()
    
    failed = []
    for f in args.files:
        if not Path(f).exists():
            continue
        try:
            header = Path(f).read_text(encoding="utf-8", errors="ignore")[:500]
            if "SPECTOR Contributors" not in header or "Proprietary" not in header:
                failed.append(f)
        except:
            pass
    
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
