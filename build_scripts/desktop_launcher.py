# -*- coding: utf-8 -*-
"""
desktop_launcher.py
Entry point used to freeze the Streamlit app into a standalone Windows/macOS/
Linux executable with PyInstaller.

Why this file exists:
Streamlit apps are normally started with the CLI command `streamlit run app.py`.
PyInstaller needs an actual Python entry point (a `if __name__ == "__main__"`
script) to freeze, so this launcher starts Streamlit's server programmatically,
then opens the user's default browser to the local app — giving a native
"double-click .exe to launch" experience.

Use build_exe.bat (Windows) or build_exe.sh (macOS/Linux) in this folder --
do not hand-roll the pyinstaller command. app.py must be passed with
--add-data, because PyInstaller freezes THIS file and so never discovers
app.py on its own; see the comments in those scripts.
"""
import os
import sys
import threading
import time
import webbrowser


def resource_path(relative_path):
    """Resolve a path correctly whether running from source or a frozen exe."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_path, relative_path)


def main():
    from streamlit.web import cli as stcli

    app_path = resource_path("app.py")
    if not os.path.exists(app_path):
        # This is what a build missing --add-data "app.py;." looks like. Fail
        # loudly here rather than letting Streamlit exit with a bare traceback
        # behind a browser window that never loads.
        sys.exit(
            f"ERROR: could not find app.py at {app_path}\n"
            "If this is a frozen build, it was packaged without app.py. "
            'Rebuild with --add-data "app.py;." (use build_scripts/build_exe.bat '
            "or build_exe.sh, which already do this)."
        )
    port = "8501"

    def open_browser():
        time.sleep(2.5)
        webbrowser.open(f"http://localhost:{port}")

    threading.Thread(target=open_browser, daemon=True).start()

    sys.argv = [
        "streamlit", "run", app_path,
        "--global.developmentMode=false",
        f"--server.port={port}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
    ]
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
