#!/usr/bin/env bash
# Build a standalone macOS/Linux executable for FrameWork.
# Run from the PROJECT ROOT folder (where app.py lives):
#   pip install -r requirements.txt
#   pip install pyinstaller
#   bash build_scripts/build_exe.sh
#
# Notes on the flags below, each of which is load-bearing:
#
#   --add-data "app.py:."    PyInstaller freezes desktop_launcher.py, so app.py
#                            is neither an analysed import nor a data file
#                            unless it is listed here. desktop_launcher.py hands
#                            app.py's path to `streamlit run`, so without this
#                            the frozen binary starts and immediately fails on a
#                            missing file.
#   --collect-all streamlit  Streamlit ships non-Python static assets and uses
#   --collect-all plotly     metadata-driven lazy imports that PyInstaller's
#   --collect-all altair     static analysis misses, producing a blank page or
#                            "Invalid distribution" at launch.

set -euo pipefail

pyinstaller --name FrameWork --onefile \
  --add-data "app.py:." \
  --add-data "data:data" \
  --add-data "pages:pages" \
  --add-data "utils:utils" \
  --add-data ".streamlit:.streamlit" \
  --collect-all streamlit \
  --collect-all plotly \
  --collect-all altair \
  build_scripts/desktop_launcher.py

echo ""
echo "Build complete. Find the FrameWork binary inside dist/"
echo ""
echo "Verify the build properly before shipping it:"
echo "  1. Run ./dist/FrameWork and confirm the app loads."
echo "  2. Earn some XP (take a quiz), then QUIT and relaunch. Your XP must"
echo "     still be there. Progress is stored under"
echo "     ~/.local/share/FrameWork/ (Linux) or"
echo "     ~/Library/Application Support/FrameWork/ (macOS) --"
echo "     never inside the PyInstaller bundle, which is deleted on exit."
