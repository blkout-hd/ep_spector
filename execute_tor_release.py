#!/usr/bin/env python3
"""
Complete SPECTOR OSS Release with Tor Integration
Executes all automation steps and pushes to GitHub.
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run command and handle errors."""
    print(f"\n{'='*70}")
    print(f"📋 {description}")
    print(f"{'='*70}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    
    print(f"✅ Success")
    return True

def main():
    """Execute complete OSS release workflow."""
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║     SPECTOR OSS RELEASE AUTOMATION - TOR INTEGRATION                    ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Change to SPECTOR directory
    spector_dir = Path("D:/DEV/SPECTOR")
    if not spector_dir.exists():
        print(f"❌ Directory not found: {spector_dir}")
        return 1
    
    import os
    os.chdir(spector_dir)
    print(f"📂 Working directory: {spector_dir}\n")
    
    steps = [
        ("git status", "Check Git status"),
        ("git remote -v", "Verify GitHub remote"),
        ("git add .", "Stage all changes"),
        ("git commit -m \"feat: add Tor integration with Tornado automation\n\n- Add TorManager for automated Tor service lifecycle\n- Add Tornado web framework integration\n- Add real-time Tor dashboard with WebSocket\n- Add SOCKS proxy support for anonymous requests\n- Add circuit management and exit node control\n- Update dependencies (tornado, stem, PySocks)\n- Add tor-admin CLI command\n- Add comprehensive Tor integration guide\n\nCo-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>\"", "Commit changes"),
        ("git push origin main", "Push to GitHub (private repo)"),
    ]
    
    for cmd, desc in steps:
        if not run_command(cmd, desc):
            print(f"\n❌ Workflow failed at: {desc}")
            return 1
    
    print("""
    
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║                  🎉 OSS RELEASE COMPLETE! 🎉                             ║
║                                                                          ║
║  ✅ Tor integration added                                                ║
║  ✅ Tornado automation configured                                        ║
║  ✅ Dependencies updated                                                 ║
║  ✅ Committed and pushed to GitHub                                       ║
║                                                                          ║
║  Next Steps:                                                             ║
║  1. Test: python launcher.py tor-admin                                   ║
║  2. Access: http://localhost:8889/tor/dashboard                          ║
║  3. Review: TOR_INTEGRATION_GUIDE.md                                     ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
    """)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
