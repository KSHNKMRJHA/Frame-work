"""Inspect the approved SignalBench real Home and lower CAN profile.

Run against a disposable app instance:
python build_scripts/check_signalbench_visual.py --url http://localhost:8501
Captures remain ignored runtime artifacts.
"""
import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

from visual_check import launch_chromium

SHOTS = Path(__file__).resolve().parent / "_shots" / "signalbench-profile"
PROBE = """() => {
 const main = document.querySelector('[data-testid="stMain"]');
 const visible = e => {const r=e.getBoundingClientRect();return r.width>0&&r.height>0;};
 const cards = [...main.querySelectorAll('[data-testid="stPageLink"]')]
   .map(e=>e.closest('[data-testid="stVerticalBlock"]'));
 return {
  overflow: document.documentElement.scrollWidth-document.documentElement.clientWidth,
  exception: [...document.querySelectorAll('[data-testid="stException"]')].map(e=>e.innerText),
  canvasImages: [...main.querySelectorAll('[data-testid="stImage"] img')].filter(visible).length,
  cards: cards.map(e=>{const s=getComputedStyle(e); return {text:e.innerText,
    border:s.borderTopWidth,radius:s.borderTopLeftRadius,shadow:s.boxShadow};})
 };
}"""


def anchor(page, locator):
    locator.scroll_into_view_if_needed()
    locator.evaluate("""e => {
      const main=document.querySelector('[data-testid="stMain"]');
      main.scrollTop += e.getBoundingClientRect().top-90;
    }""")
    page.wait_for_timeout(250)


def capture(page, theme, width, section, records, full=False):
    state = page.evaluate(PROBE)
    assert not state["exception"], state["exception"]
    assert state["overflow"] <= 2, (theme, width, section, state)
    filename = f"signalbench-revision-{theme}-{width}-{section}.png"
    if full:
        page.locator('[data-testid="stMainBlockContainer"]').screenshot(path=str(SHOTS / filename))
    else:
        page.screenshot(path=str(SHOTS / filename))
    records.append({"file": filename, "theme": theme, "width": width, "section": section, **state})


def run(url):
    SHOTS.mkdir(parents=True, exist_ok=True)
    records = []
    with sync_playwright() as p:
        browser, which = launch_chromium(p)
        for scheme in ("dark", "light"):
            for width in (1440, 900, 390):
                ctx = browser.new_context(viewport={"width": width, "height": 1000}, color_scheme=scheme)
                page = ctx.new_page()
                page.goto(url, wait_until="networkidle")
                page.wait_for_timeout(2500)
                if page.get_by_role("dialog").count():
                    page.get_by_role("button", name="Skip", exact=True).click()
                    page.wait_for_timeout(700)
                if width == 390:
                    sidebar = page.locator('[data-testid="stSidebar"]')
                    if sidebar.is_visible() and sidebar.bounding_box()["x"] >= 0:
                        sidebar.locator('button[data-testid="stBaseButton-headerNoPadding"]').click()
                        page.wait_for_timeout(400)
                # Inspect the actual pill style; quoted font names must not truncate it.
                chip = page.locator('[data-testid="stMain"] span').filter(has_text="v1.1.1").first
                css = chip.evaluate("""e => {const s=getComputedStyle(e);return {
                    background:s.backgroundColor,border:s.borderTopWidth,radius:s.borderRadius,
                    size:s.fontSize,text:e.innerText};}""")
                assert css["background"] != "rgba(0, 0, 0, 0)", css
                assert css["border"] == "1px" and css["radius"] == "999px", css
                assert float(css["size"].rstrip("px")) <= 14, css
                capture(page, scheme, width, "home", records)
                records[-1]["versionChip"] = css
                links = page.locator('[data-testid="stMain"] [data-testid="stPageLink"]')
                assert links.count() == 12, links.count()
                descriptions = page.locator('[data-testid="stMain"] div[style*="font-size: 0.9rem"]')
                assert descriptions.count() == 12
                assert all(value.strip() for value in descriptions.all_text_contents())
                assert len(records[-1]["cards"]) == 12
                for card in records[-1]["cards"]:
                    assert card["border"] == "1px" and card["radius"] in ("6.4px", "8px"), card
                    assert card["shadow"] == "none", card
                anchor(page, descriptions.first)
                capture(page, scheme, width, "home-nav", records)
                page.goto(f"{url}/Encyclopedia?p=can", wait_until="networkidle")
                page.wait_for_timeout(2500)
                capture(page, scheme, width, "encyclopedia-top", records)
                hero = page.get_by_text("CAN (Controller Area Network)", exact=True)
                assert hero.inner_text() == "CAN (Controller Area Network)"
                anchor(page, hero)
                capture(page, scheme, width, "identity-spec", records)
                for section, label in (
                    ("electrical", "⚡ Electrical & Hardware Profile"),
                    ("conductors", "🔌 Wiring & signals"),
                    ("levels", "⚡ Electrical characteristics"),
                ):
                    anchor(page, page.get_by_role("heading", name=label, exact=True))
                    capture(page, scheme, width, section, records)
                for section, tab in (
                    ("frame", "📦 Frame / Packet Structure"),
                    ("topology", "🕸️ Network Topology"),
                    ("waveform", "📈 Signal Waveform"),
                ):
                    page.get_by_role("tab", name=tab, exact=True).click()
                    page.wait_for_timeout(600)
                    if section == "frame" and width == 390:
                        page.get_by_text("Frame field values", exact=True).click()
                        page.wait_for_timeout(300)
                    anchor(page, page.get_by_role("heading", name="🖼️ Interactive Diagrams", exact=True))
                    capture(page, scheme, width, section, records)
                    assert records[-1]["canvasImages"] >= 1, (scheme, width, section)
                if width == 390:
                    capture(page, scheme, width, "profile-full", records, full=True)
                ctx.close()
        browser.close()
    report = {"browser": which, "captures": records}
    (SHOTS / "signalbench-revision-review.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"SignalBench visual checks passed: {len(records)} captures, both themes, 1440/900/390px")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8501")
    run(parser.parse_args().url.rstrip("/"))
