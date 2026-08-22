#!/usr/bin/env python3
"""Put everything back. Restores the newest backups/<timestamp>/ snapshot,
or one you name: ./uninstall.py 20260822-141500
"""
import os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
BACKUPS = os.path.join(ROOT, "backups")

def main():
    if not os.path.isdir(BACKUPS) or not os.listdir(BACKUPS):
        sys.exit("no backups to restore from")
    stamp = sys.argv[1] if len(sys.argv) > 1 else sorted(os.listdir(BACKUPS))[-1]
    snap = os.path.join(BACKUPS, stamp)
    if not os.path.isdir(snap):
        sys.exit(f"no such backup: {stamp}\nhave: {', '.join(sorted(os.listdir(BACKUPS)))}")
    print(f"restoring {stamp}")

    term = os.path.join(snap, "com.apple.Terminal.plist")
    if os.path.exists(term):
        with open(term, "rb") as f:
            subprocess.run(["defaults", "import", "com.apple.Terminal", "-"], input=f.read())
        print("  ✔ Terminal.app prefs")

    home_snap = os.path.join(snap, "home")
    for dirpath, _, files in os.walk(home_snap):
        for name in files:
            src = os.path.join(dirpath, name)
            dest = os.path.join(HOME, os.path.relpath(src, home_snap))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(src, dest)
            print(f"  ✔ {dest.replace(HOME, '~')}")

    ext = os.path.join(HOME, ".vscode", "extensions")
    for d in os.listdir(ext) if os.path.isdir(ext) else []:
        if d.startswith("local.neonferatu-"):
            shutil.rmtree(os.path.join(ext, d))
            print(f"  ✔ removed {d}")

    subprocess.run(["killall", "cfprefsd"], capture_output=True)
    print("\ndone — restart the apps you had open.")

if __name__ == "__main__":
    main()
