# -*- coding: utf-8 -*-
"""
sync_mobile.py
Copies the two files the Kivy mobile companion duplicates from the desktop app:

    data/protocols.json   -> kivy_mobile/data/protocols.json
    utils/quiz_engine.py  -> kivy_mobile/quiz_logic.py

Buildozer packages only what lives under kivy_mobile/, so those copies cannot
be symlinks or imports. Without this script the two trees drift apart silently
and the mobile app keeps teaching whatever the desktop app has since fixed.

Run after any change to the protocol database or the quiz engine:

    python build_data.py && python build_scripts/sync_mobile.py

CI fails if the copies are stale (see .github/workflows/ci.yml).
"""
import filecmp
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAIRS = [
    (os.path.join(ROOT, "data", "protocols.json"),
     os.path.join(ROOT, "kivy_mobile", "data", "protocols.json")),
    (os.path.join(ROOT, "utils", "quiz_engine.py"),
     os.path.join(ROOT, "kivy_mobile", "quiz_logic.py")),
]


def main():
    changed = 0
    for src, dst in PAIRS:
        if not os.path.exists(src):
            print(f"ERROR: source missing: {src}", file=sys.stderr)
            return 1
        rel_src = os.path.relpath(src, ROOT)
        rel_dst = os.path.relpath(dst, ROOT)
        if os.path.exists(dst) and filecmp.cmp(src, dst, shallow=False):
            print(f"  up to date  {rel_dst}")
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        print(f"  synced      {rel_src} -> {rel_dst}")
        changed += 1

    print(f"{changed} file(s) updated." if changed else "Mobile companion already in sync.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
