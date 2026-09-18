@echo off
REM Build a standalone Windows .exe for FrameWork.
REM Run this from the PROJECT ROOT folder (where app.py lives), on Windows,
REM with a Python environment that has pyinstaller and all requirements.txt
REM packages installed:
REM     pip install -r requirements.txt
REM     pip install pyinstaller
REM Then run:
REM     build_scripts\build_exe.bat
REM
REM Notes on the flags below, each of which is load-bearing:
REM
REM   --add-data "app.py;."   PyInstaller freezes desktop_launcher.py, so app.py
REM                           is neither an analysed import nor a data file
REM                           unless it is listed here. desktop_launcher.py
REM                           hands app.py's path to `streamlit run`, so without
REM                           this the frozen .exe starts and immediately fails
REM                           on a missing file - and with --noconsole the user
REM                           sees nothing at all.
REM   --collect-all streamlit Streamlit ships non-Python static assets and uses
REM   --collect-all plotly    metadata-driven lazy imports that PyInstaller's
REM   --collect-all altair    static analysis misses, producing a blank page or
REM                           "Invalid distribution" at launch.
REM   --console               Streamlit's server writes to stdout/stderr. With
REM                           --noconsole those are None on Windows and the
REM                           server can die on its first write. Keep the
REM                           console window; see the note at the bottom for
REM                           hiding it properly if you want that.

REM Stamp the build number first. A frozen .exe has no .git, so utils/branding.py
REM reads utils/_build_stamp.txt (bundled below via --add-data "utils;utils")
REM instead -- without this the packaged app would not know its own commit.
python build_scripts\stamp_build.py
if errorlevel 1 goto :stamp_failed

pyinstaller --name FrameWork --onefile --console ^
  --add-data "app.py;." ^
  --add-data "data;data" ^
  --add-data "pages;pages" ^
  --add-data "utils;utils" ^
  --add-data ".streamlit;.streamlit" ^
  --collect-all streamlit ^
  --collect-all plotly ^
  --collect-all altair ^
  build_scripts\desktop_launcher.py

echo.
echo Build complete. Find FrameWork.exe inside the dist\ folder.
echo.
echo Verify the build properly before shipping it:
echo   1. Run dist\FrameWork.exe and confirm the app loads.
echo   2. Earn some XP (take a quiz), then QUIT and relaunch. Your XP must
echo      still be there. Progress is stored under
echo      %%LOCALAPPDATA%%\FrameWork\user_state.json -- never
echo      inside the PyInstaller bundle, which is deleted on exit.
echo.
echo To hide the console window, build a proper windowed launcher that
echo redirects sys.stdout/sys.stderr to a log file before starting Streamlit,
echo rather than just swapping --console for --noconsole.
exit /b 0

:stamp_failed
echo ERROR: build_scripts\stamp_build.py failed. Is Python on PATH?
exit /b 1
