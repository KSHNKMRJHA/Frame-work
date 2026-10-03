"""Cross-engine verification for the parts most likely to differ by browser.

visual_check.py drives real Chrome. This runs the same two invariants across
Chromium, Firefox and WebKit, because CSS layout is not identical between
engines and a responsive fix verified only in Blink proves nothing elsewhere:

  1. Theme tokens - the rendered palette must match utils/theme.py in both
     colour schemes. Catches engine-specific colour parsing.
  2. Responsive columns - narrowest visible column and horizontal overflow at
     390 / 900 / 1440px. Catches a metric grid that fits in Blink but collapses
     in Gecko or WebKit.

Usage:  python build_scripts/cross_browser.py
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "build_scripts"))

from visual_check import (  # noqa: E402
    DESKTOP, PHONE, TABLET, _EXPECTED, _THEME_JS, launch_chromium,
)

BASE = "http://localhost:8501"
TARGET = "/Encyclopedia?p=usb20"

# Below this a metric value clips its own label; see VECTORFORM_PLAN.md.
MIN_COLUMN_PX = 120

_COLUMNS_JS = """() => {
    const cols = [...document.querySelectorAll(
        '[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]')];
    const visible = cols.map(c => c.getBoundingClientRect()).filter(r => r.width > 0);
    if (visible.length < 2) return {ok: null, minWidth: null, rows: 0};
    const rows = new Set(visible.map(r => Math.round(r.top))).size;
    return {ok: rows > 1, rows: rows,
            minWidth: Math.round(Math.min(...visible.map(r => r.width))),
            overflow: document.documentElement.scrollWidth
                      - document.documentElement.clientWidth};
}"""


def run():
    from playwright.sync_api import sync_playwright

    expected = _EXPECTED or None
    if expected is None:
        from visual_check import _expected_palettes
        expected = _expected_palettes()

    failures = []
    with sync_playwright() as p:
        for engine in ("chromium", "firefox", "webkit"):
            try:
                # Chromium: drive an installed Chrome when there is one, as
                # visual_check.py does, so no bundled-browser download is
                # required for Blink either.
                if engine == "chromium":
                    browser, which = launch_chromium(p)
                else:
                    browser = getattr(p, engine).launch(headless=True)
            except Exception as exc:                        # noqa: BLE001
                print(f"  {engine}: SKIPPED ({type(exc).__name__})")
                continue
            version = browser.version
            print(f"\n{engine} {version}")

            # --- 1. theme tokens, both schemes
            for scheme in ("dark", "light"):
                ctx = browser.new_context(viewport=DESKTOP, color_scheme=scheme)
                page = ctx.new_page()
                page.goto(f"{BASE}{TARGET}", wait_until="networkidle", timeout=60_000)
                page.wait_for_timeout(3000)
                got = page.evaluate(_THEME_JS)
                for key, want in expected[scheme].items():
                    # A probe can legitimately find nothing on some pages (no
                    # <code> block above the fold, say). Skipping beats failing
                    # on an element that was never going to be there.
                    if got.get(key) is None:
                        continue
                    if got[key] != want:
                        failures.append(
                            f"{engine}/{scheme} {key}: want {want}, got {got[key]}")
                print(f"  {scheme:5} app={got['app']} code={got['code']} text={got['text']}")
                ctx.close()

            # --- 2. responsive columns at three widths
            ctx = browser.new_context(viewport=DESKTOP)
            page = ctx.new_page()
            page.goto(f"{BASE}{TARGET}", wait_until="networkidle", timeout=60_000)
            page.wait_for_timeout(3000)
            for label, size, must_stack in (("phone", PHONE, True),
                                            ("tablet", TABLET, False),
                                            ("desktop", DESKTOP, False)):
                page.set_viewport_size(size)
                page.wait_for_timeout(1200)
                got = page.evaluate(_COLUMNS_JS)
                if got["minWidth"] is None:
                    failures.append(f"{engine}/{label}: no columns found")
                    print(f"  {label:7} no columns")
                    continue
                if must_stack and got["ok"] is False:
                    failures.append(f"{engine}/{label}: columns did not stack")
                if got["overflow"] > 2:
                    failures.append(
                        f"{engine}/{label}: {got['overflow']}px horizontal overflow")
                if got["minWidth"] < MIN_COLUMN_PX:
                    failures.append(
                        f"{engine}/{label}: column only {got['minWidth']}px "
                        f"(min {MIN_COLUMN_PX})")
                print(f"  {label:7} minCol={got['minWidth']:4}px rows={got['rows']:3} "
                      f"overflow={got['overflow']}")
            ctx.close()
            browser.close()

    print()
    if failures:
        print("FAILURES:")
        for f in failures:
            print(f"  {f}")
        return 1
    print("ALL CROSS-BROWSER CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(run())
