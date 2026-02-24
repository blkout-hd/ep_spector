#!/usr/bin/env python3
import sys
import json
from pathlib import Path
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", default=[])
    args = parser.parse_args()
    
    errors = 0
    for f in args.files:
        if not Path(f).exists():
            continue
        try:
            for line in Path(f).read_text(encoding="utf-8").splitlines():
                if line.strip():
                    json.loads(line)
        except json.JSONDecodeError:
            errors += 1
            print(f"❌ {f}: Invalid JSON")
    
    return 1 if errors > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
