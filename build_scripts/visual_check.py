# -*- coding: utf-8 -*-
"""Visual verification of the Vectorform UI against a running Streamlit app.

Drives the *installed* Chrome through Playwright, so no browser download is
needed. Captures screenshots at desktop / tablet / phone widths and asserts
the things unit tests cannot: that the stylesheet actually applies, that
conductor cards render, and that columns stack on a narrow viewport.

    python build_scripts/visual_check.py [--url http://localhost:8501]

Screenshots land in `build_scripts/_shots/`.
"""
import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHOTS = ROOT / "build_scripts" / "_shots"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

DESKTOP = {"width": 1440, "height": 1000}
TABLET = {"width": 900, "height": 1100}
PHONE = {"width": 390, "height": 900}

# Read the palette Streamlit actually rendered. These must match utils/theme.py
# and .streamlit/config.toml exactly - a drift here means the two sources of
# truth have diverged.
_THEME_JS = """() => {
    const bg = s => { const e = document.querySelector(s);
        return e ? getComputedStyle(e).backgroundColor : null; };
    const col = s => { const e = document.querySelector(s);
        return e ? getComputedStyle(e).color : null; };
    // null, not 'n/a': a probe may legitimately find no <code> on a given page
    // state, and callers must skip a null rather than read it as a mismatch.
    return {app: bg('.stApp'),
            sidebar: bg('[data-testid="stSidebar"]'),
            code: col('code'),
            text: col('.stApp')};
}"""


def _hex_to_rgb(value):
    """'#0b1220' -> 'rgb(11, 18, 32)' to compare with computed styles."""
    value = value.lstrip("#")
    r, g, b = (int(value[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgb({r}, {g}, {b})"


def _expected_palettes():
    """Build expectations from the single token source of truth."""
    from utils import theme

    return {
        "dark": {
            "app": _hex_to_rgb(theme.DARK["bg"]),
            "sidebar": _hex_to_rgb(theme.DARK["bg_alt"]),
            "code": _hex_to_rgb(theme.DARK["signal"]),
            "text": _hex_to_rgb(theme.DARK["text"]),
        },
        "light": {
            "app": _hex_to_rgb(theme.LIGHT["bg"]),
            "sidebar": _hex_to_rgb(theme.LIGHT["bg_alt"]),
            "code": _hex_to_rgb(theme.LIGHT["signal"]),
            "text": _hex_to_rgb(theme.LIGHT["text"]),
        },
    }


_EXPECTED = None          # populated inside run() once sys.path is set


def log(rows, text):
    """Print ASCII-safe: this console is cp1252 and cannot encode the UI glyphs."""
    rows.append(text)
    print(text.encode("ascii", "replace").decode("ascii"))


def probe_tokens(page):
    """Read the theme off the live page.

    Checks the *rendered* background of the app shell plus any inline-styled
    component. The :root custom properties are reported too, but they are NOT
    asserted on: Streamlit 1.64 strips injected <style> blocks, so the
    stylesheet is progressive enhancement only.
    """
    return page.evaluate(
        """() => {
            const cs = getComputedStyle(document.documentElement);
            // The theme lands on the .stApp shell, not stAppViewContainer.
            const app = document.querySelector('.stApp');
            return {
                accent: cs.getPropertyValue('--fw-accent').trim(),
                bg: cs.getPropertyValue('--fw-bg').trim(),
                appBg: app ? getComputedStyle(app).backgroundColor : '',
                bodyColor: getComputedStyle(document.body).color,
            };
        }"""
    )


def probe_tabular(page):
    return page.evaluate(
        """() => {
            const m = document.querySelector('[data-testid="stMetricValue"]');
            if (!m) return 'no-metric';
            const s = getComputedStyle(m);
            return (s.fontVariantNumeric || '') + '|' + (s.fontFeatureSettings || '');
        }"""
    )


def probe_columns(page):
    """Measure the st.column flex layout across every column on the page.

    Checking only columns[0] and columns[1] misses partial wrapping, where some
    columns drop to a second row while others stay put. Distinct `top` values
    expose that, and the narrowest column is reported because a layout can
    "stack" while still being unusably thin.
    """
    return page.evaluate(
        """() => {
            const cols = [...document.querySelectorAll(
                '[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]')];
            if (cols.length < 2) return {ok: null, n: cols.length, rows: 0,
                                         minWidth: null, hidden: 0, overflow: 0};
            // Streamlit keeps inactive st.tabs mounted with zero width, so they
            // must be excluded or they make every layout look unusably narrow.
            const rects = cols.map(c => c.getBoundingClientRect());
            const visible = rects.filter(r => r.width > 0);
            if (visible.length < 2) return {ok: null, n: cols.length, rows: 0,
                                            minWidth: null, hidden: cols.length,
                                            overflow: 0};
            const rows = new Set(visible.map(r => Math.round(r.top))).size;
            return {ok: rows > 1, n: visible.length, rows: rows,
                    minWidth: Math.round(Math.min(...visible.map(r => r.width))),
                    hidden: cols.length - visible.length,
                    overflow: document.documentElement.scrollWidth
                              - document.documentElement.clientWidth};
        }"""
    )


def texts(page, selector, attr=None):
    js = "els => els.map(e => (e.textContent || '').trim())"
    return page.eval_on_selector_all(selector, js)


def run(url):
    from playwright.sync_api import sync_playwright

    global _EXPECTED
    sys.path.insert(0, str(ROOT))
    _EXPECTED = _expected_palettes()

    SHOTS.mkdir(parents=True, exist_ok=True)
    rows, failures, errors = [], [], []

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, headless=True)
        page = browser.new_page(viewport=DESKTOP)
        page.on("pageerror", lambda e: errors.append(str(e)))

        # --- 1. Does the stylesheet actually apply? -----------------------
        page.goto(url, wait_until="networkidle", timeout=60_000)
        page.wait_for_timeout(3500)

        tok = probe_tokens(page)
        log(rows, f"app bg={tok['appBg']} body text={tok['bodyColor']} "
                  f"(css vars: accent={tok['accent'] or 'stripped'})")
        if tok["appBg"] in ("", "rgba(0, 0, 0, 0)", "transparent"):
            failures.append("app shell has no background - theme not applied")

        tab = probe_tabular(page)
        log(rows, f"metric typography: {tab}")
        if tab == "no-metric":
            failures.append("no st.metric found to style")

        groups = page.evaluate(
            """() => [...document.querySelectorAll('div')]
                .map(e => (e.textContent||'').trim())
                .filter(t => ['Reference','Context','Practice','Meta'].includes(t))"""
        )
        # The built-in Streamlit nav is the single source; assert it exists and
        # that we have NOT added a duplicate grouped list beside it.
        nav_links = page.evaluate(
            """() => [...document.querySelectorAll('[data-testid="stSidebarNav"] a')]
                .map(a => (a.textContent||'').trim()).filter(Boolean)"""
        )
        dupes = sorted(set(g for g in groups if nav_links.count(g) > 0))
        log(rows, f"sidebar nav links: {len(nav_links)} {nav_links[:4]}")
        if len(nav_links) < 6:
            failures.append(f"sidebar nav has only {len(nav_links)} links")
        if dupes:
            failures.append(f"duplicated sidebar entries: {dupes}")

        page.screenshot(path=str(SHOTS / "01_home_desktop.png"))
        log(rows, "shot 01 home desktop 1440px")

        # --- 2. Deep link straight to a protocol --------------------------
        page.goto(f"{url}/Encyclopedia?p=usb20", wait_until="networkidle",
                  timeout=60_000)
        page.wait_for_timeout(4500)
        h1 = page.inner_text("h1").strip()
        log(rows, f"deep link h1: {h1!r}")
        if "USB" not in page.content():
            failures.append("deep link ?p=usb20 did not surface USB content")

        cards = texts(page, "[style*='monospace'], [style*='mono']")
        card_colour = page.evaluate(
            """() => {
                const el = [...document.querySelectorAll('span')]
                    .find(e => /^(D[+-])$/.test((e.textContent||'').trim()));
                return el ? getComputedStyle(el).color : '';
            }"""
        )
        log(rows, f"conductor cards: {len(cards)} -> {cards[:6]}")
        log(rows, f"D+ computed colour: {card_colour}")
        if not cards:
            failures.append("no conductor cards rendered")
        if not card_colour:
            failures.append("conductor card not styled (inline styles stripped)")

        badge_text = page.evaluate(
            """() => [...document.querySelectorAll('div')]
                .filter(e => (e.textContent||'').trim().startsWith('\u21c4'))
                .map(e => e.textContent.trim()).slice(0,3)"""
        )
        log(rows, f"pair badges: {badge_text}")
        if not badge_text:
            failures.append("no differential pair badge rendered")

        bars = texts(page, "[style*='tabular-nums']")
        log(rows, f"voltage bars: {len(bars)} -> {bars[:4]}")
        if not bars:
            failures.append("no voltage bars rendered")

        page.screenshot(path=str(SHOTS / "02_encyclopedia_usb.png"))
        log(rows, "shot 02 encyclopedia USB")

        # --- 3. Responsive -------------------------------------------------
        # Phone MUST stack. Tablet is wide enough that Streamlit legitimately
        # keeps columns side by side, so it is asserted for overflow and
        # usability instead of stacking. Both are enforced - a logged-but-
        # unchecked result previously let a tablet failure pass unnoticed.
        for label, size, must_stack, shot in (
            ("phone", PHONE, True, "03_usb_phone.png"),
            ("tablet", TABLET, False, "04_usb_tablet.png"),
        ):
            page.set_viewport_size(size)
            page.wait_for_timeout(1500)
            got = probe_columns(page)
            log(rows, f"{label} {size['width']}px columns: {got}")
            if got["ok"] is None:
                failures.append(f"no st.columns found at {label} width")
                continue
            if must_stack and got["ok"] is False:
                failures.append(f"columns did NOT stack at {size['width']}px")
            if got["overflow"] > 2:
                failures.append(
                    f"horizontal overflow of {got['overflow']}px at "
                    f"{size['width']}px")
            if got["minWidth"] is not None and got["minWidth"] < 120:
                failures.append(
                    f"column only {got['minWidth']}px wide at {size['width']}px "
                    "- too narrow to read")
            page.screenshot(path=str(SHOTS / shot))

        # --- 4. Both colour schemes --------------------------------------
        # Streamlit follows prefers-color-scheme natively, so emulate each and
        # assert the rendered palette matches utils/theme.py exactly.
        for scheme in ("dark", "light"):
            ctx = browser.new_context(viewport=DESKTOP, color_scheme=scheme)
            sp = ctx.new_page()
            sp.goto(f"{url}/Encyclopedia?p=usb20", wait_until="networkidle",
                    timeout=60_000)
            sp.wait_for_timeout(3500)
            got = sp.evaluate(_THEME_JS)
            log(rows, f"{scheme:5}: app={got['app']} sidebar={got['sidebar']} "
                       f"code={got['code']} text={got['text']}")
            for key, expected in _EXPECTED[scheme].items():
                if got.get(key) is None:
                    # Element absent in this page state; nothing to compare.
                    log(rows, f"  skip {key}: not present on this page")
                    continue
                if got[key] != expected:
                    failures.append(
                        f"{scheme} {key}: expected {expected}, got {got[key]}")
            sp.screenshot(path=str(SHOTS / f"06_{scheme}_usb.png"))
            log(rows, f"shot 06 {scheme} theme")
            ctx.close()

        page.goto(f"{url}/Settings", wait_until="networkidle", timeout=60_000)
        page.wait_for_timeout(3000)
        page.screenshot(path=str(SHOTS / "07_settings.png"))
        log(rows, "shot 07 settings page")

        browser.close()

    if errors:
        log(rows, f"page errors: {errors[:3]}")
        failures.append(f"{len(errors)} uncaught page error(s)")

    log(rows, "")
    log(rows, "FAILURES:\n  " + "\n  ".join(failures) if failures
        else "ALL VISUAL CHECKS PASSED")
    (ROOT / "visual_report.txt").write_text("\n".join(rows), encoding="utf-8")
    return 1 if failures else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8501")
    sys.exit(run(ap.parse_args().url))
