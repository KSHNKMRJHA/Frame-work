"""Sweep every page for the responsive defect found on Encyclopedia.

The 62px metric-column bug was page-specific, but the *pattern* that caused it
is not: weighted splits like st.columns([2, 1]) and st.columns(4) repeat across
the app, and Streamlit only auto-stacks below ~640px. So at 900px any such
row can collapse the same way. This walks all pages and reports the narrowest
visible column and any horizontal overflow on each.

Usage:  python build_scripts/page_sweep.py [width]
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "build_scripts"))

from visual_check import CHROME  # noqa: E402

BASE = "http://localhost:8501"

# Streamlit derives the route from the filename prefix, stripping the leading
# index and the emoji: "4_📖_Glossary.py" -> "/Glossary".
PAGES = [
    "Encyclopedia", "Compare", "Selector", "Glossary", "Timeline_History",
    "Mindmap", "Geography_Origins", "Quiz_Assessment", "Puzzles_Games",
    "Science_Math_Lab", "Settings_Profile", "Info",
]

MIN_COLUMN_PX = 120

# Detects text that is genuinely cut off, not merely a narrow box.
#
# Streamlit clips with `overflow: visible` + `text-overflow: clip`, so
# scrollWidth == clientWidth and Range.getClientRects() returns the *line box*
# rather than the glyph run - neither technique notices that "-3.55%" is being
# shown as "-3....". Measuring the string with canvas at the element's own
# computed font is the only reliable signal, and it is what caught the 90px
# metric regression.
#
# Restricted to single-line leaf elements: multi-line text wraps (fine) rather
# than truncates, and would false-positive.
_JS = r"""() => {
    const cv = document.createElement('canvas').getContext('2d');
    const sel = ['[data-testid="stMetricValue"]', '[data-testid="stMetricLabel"]',
                 'h1', 'h2', 'h3', 'h4', 'p', 'label', 'button', 'summary'];
    const clipped = [];
    document.querySelectorAll(sel.join(',')).forEach(e => {
      if (e.children.length) return;                    // leaf text only
      const txt = (e.textContent || '').trim();
      if ((txt.match(/[A-Za-z0-9]/g) || []).length < 2) return;   // emoji/icon
      const cs = getComputedStyle(e);
      const fs = parseFloat(cs.fontSize) || 0;
      if (!fs) return;
      const lh = parseFloat(cs.lineHeight) || fs * 1.2;
      const h = e.getBoundingClientRect().height;
      if (h > lh * 1.6) return;                         // wraps, not clipped
      const avail = e.clientWidth;
      if (avail <= 40) return;                          // icon-sized box
      cv.font = cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily;
      const need = cv.measureText(txt).width;
      if (need > avail + 1) {
        clipped.push({txt: txt.slice(0, 34), avail: Math.round(avail),
                      need: Math.round(need)});
      }
    });
    return clipped.slice(0, 6);
}"""


def sweep(width, height=1200):
    from playwright.sync_api import sync_playwright

    problems = []
    with sync_playwright() as p:
        launch = {"executable_path": CHROME} if os.path.exists(CHROME) else {}
        browser = p.chromium.launch(headless=True, **launch)
        ctx = browser.new_context(viewport={"width": width, "height": height})
        page = ctx.new_page()
        for route in PAGES:
            try:
                page.goto(f"{BASE}/{route}", wait_until="networkidle", timeout=60_000)
                page.wait_for_timeout(2600)
            except Exception as exc:                          # noqa: BLE001
                print(f"  {route:20} ERROR {type(exc).__name__}")
                problems.append(f"{route}: {type(exc).__name__}")
                continue
            clipped = page.evaluate(_JS)
            overflow = page.evaluate(
                "() => document.documentElement.scrollWidth"
                " - document.documentElement.clientWidth")
            flag = ""
            if overflow > 2:
                flag += f"  OVERFLOW {overflow}px"
                problems.append(f"{route}: {overflow}px horizontal overflow")
            if clipped:
                flag += f"  CLIPPED {len(clipped)}"
                for c in clipped:
                    # Protocol names carry emoji; the Windows console is cp1252
                    # and would raise on them, so keep the report ASCII-safe.
                    t = c["txt"].encode("ascii", "replace").decode()
                    problems.append(
                        f"{route}: '{t}' needs {c['need']}px "
                        f"but has {c['avail']}px")
            print(f"  {route:20} clipped={len(clipped):2} ovf={overflow}{flag}")
            for c in clipped:
                t = c["txt"].encode("ascii", "replace").decode()
                print(f"       needs {c['need']:4}px, has {c['avail']:4}px  {t!r}")
        ctx.close()
        browser.close()
    return problems


if __name__ == "__main__":
    w = int(sys.argv[1]) if len(sys.argv) > 1 else 900
    print(f"\nsweeping all pages at {w}px\n")
    found = sweep(w)
    print()
    if found:
        print(f"{len(found)} PROBLEM(S) at {w}px:")
        for f in found:
            print(f"  {f}")
        sys.exit(1)
    print(f"no clipped text and no horizontal overflow at {w}px")
