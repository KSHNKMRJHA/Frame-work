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
    // Owner roles deliberately exclude bare `p`: a paragraph inside a metric
    // sizes itself to its own content, so measuring it against its own width
    // can never fail. The clipping box is the nearest *ancestor* role - for
    // Streamlit that is stMetricValue. Plain paragraphs are skipped because
    // body text wraps rather than truncates.
    const sel = ['[data-testid="stMetricValue"]', '[data-testid="stMetricLabel"]',
                 'h1', 'h2', 'h3', 'h4', 'button', 'label', 'summary',
                 'li', 'th', 'td'];
    const roots = document.querySelectorAll(sel.join(','));
    const out = [];
    const seen = new Set();
    const match = sel.join(',');

    // Walk TEXT nodes, not elements. Streamlit wraps a metric value in a child
    // span, so a "leaf elements only" filter silently skipped every
    // stMetricValue on the page - the sweep reported clean while a real 90px
    // regression was on screen.
    //
    // Two different elements matter and must not be conflated:
    //   renderer - the element the text is actually painted by; its font sizes
    //               the glyphs, so canvas measureText must use it.
    //   owner     - the nearest matching ancestor; its clientWidth is the box
    //               the text gets clipped against.
    const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let node = walk.nextNode(); node; node = walk.nextNode()) {
      const txt = (node.textContent || '').trim();
      if (!txt || (txt.match(/[A-Za-z0-9]/g) || []).length < 2) continue;
      const renderer = node.parentElement;
      if (!renderer) continue;
      const owner = renderer.closest(match);
      if (!owner || seen.has(owner)) continue;
      seen.add(owner);
      const rcs = getComputedStyle(renderer);
      const fs = parseFloat(rcs.fontSize) || 0;
      if (!fs) continue;
      const lh = parseFloat(rcs.lineHeight) || fs * 1.2;
      if (owner.getBoundingClientRect().height > lh * 1.6) continue;  // wraps
      const avail = owner.clientWidth;
      if (avail <= 40) continue;                                       // icon
      cv.font = rcs.fontWeight + ' ' + rcs.fontSize + ' ' + rcs.fontFamily;
      const need = cv.measureText(txt).width;
      if (need > avail + 1) {
        out.push({txt: txt.slice(0, 34), avail: Math.round(avail),
                  need: Math.round(need)});
      }
    }
    return out.slice(0, 8);
}"""

# Reveals collapsed content. Streamlit expanders are <details> elements, and
# hiding their contents from the measurement hides every defect inside them.
_OPEN_ALL = """() => {
    let n = 0;
    document.querySelectorAll('details').forEach(d => {
        if (!d.open) { d.open = true; n++; }
    });
    return n;
}"""

# Clicks the nth st.tab, returning false when there is no such tab. Tab panels
# that are not selected render at zero width, so each has to be visited.
_click_tab = """idx => {
    const tabs = document.querySelectorAll('[data-testid="stTab"]');
    if (idx >= tabs.length) return false;
    tabs[idx].click();
    return true;
}"""


def measure(page):
    """Return (clipped_text, horizontal_overflow) for the current view."""
    return page.evaluate(_JS), page.evaluate(
        "() => document.documentElement.scrollWidth"
        " - document.documentElement.clientWidth")


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

            # Measure the collapsed view *and* every revealed state. Science Lab
            # keeps its calculators inside a collapsed <details>, so a
            # first-paint-only sweep reported "clean" while the very metrics
            # that were broken sat unmeasured in the DOM.
            states = [("collapsed",)]
            if page.evaluate(_OPEN_ALL):
                page.wait_for_timeout(900)
                states.append(("expanded",))
            states += [(f"tab:{i}",) for i in range(12)
                       if page.evaluate(_click_tab, i)]

            total_clipped, worst_overflow = 0, 0
            for (state,) in states:
                if state.startswith("tab:"):
                    page.evaluate(_click_tab, int(state.split(":")[1]))
                    page.wait_for_timeout(700)
                clipped, overflow = measure(page)
                total_clipped += len(clipped)
                worst_overflow = max(worst_overflow, overflow)
                for c in clipped:
                    # Protocol names carry emoji; the Windows console is cp1252
                    # and would raise on them, so keep the report ASCII-safe.
                    t = c["txt"].encode("ascii", "replace").decode()
                    problems.append(
                        f"{route} [{state}]: '{t}' needs {c['need']}px "
                        f"but has {c['avail']}px")
                if overflow > 2:
                    problems.append(
                        f"{route} [{state}]: {overflow}px horizontal overflow")
            print(f"  {route:20} states={len(states):2} clipped={total_clipped:2} "
                  f"ovf={worst_overflow}")
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
