#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Execute every Streamlit page in-process and report failures.

Streamlit pages are just scripts, so `runpy` surfaces import errors, syntax
errors and anything raised at module level — without needing a browser. Run it
after any UI change:

    python build_scripts/smoke_pages.py

Exit code is non-zero when any page fails, so CI can gate on it.
"""
import io
import pathlib
import runpy
import sys
import traceback

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main():
    targets = ["app.py"] + sorted(
        str(p.relative_to(ROOT)) for p in (ROOT / "pages").glob("*.py")
    )
    ok, failures = 0, []
    report = io.StringIO()

    for target in targets:
        try:
            runpy.run_path(str(ROOT / target), run_name="__main__")
            report.write(f"  ok    {target}\n")
            ok += 1
        except SystemExit:
            report.write(f"  ok    {target} (clean exit)\n")
            ok += 1
        except Exception as exc:                      # noqa: BLE001 - report all
            report.write(f"  FAIL  {target}: {type(exc).__name__}: {exc}\n")
            for line in traceback.format_exc().splitlines()[-4:]:
                report.write("          " + line + "\n")
            failures.append(target)

    report.write(f"\npages: {ok} ok, {len(failures)} failed\n")
    # Write via UTF-8 so emoji in tracebacks cannot crash the reporter.
    (ROOT / "smoke_report.txt").write_text(report.getvalue(), encoding="utf-8")
    sys.stdout.write(report.getvalue().encode("ascii", "replace").decode("ascii"))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
