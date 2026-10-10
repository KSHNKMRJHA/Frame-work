"""All-page SignalBench matrix, including tabs and all calculator outputs.

Run only against a disposable app instance: browser visits can award learner XP.
Captures and measurements are ignored runtime artifacts under _shots/rollout.
"""
import argparse
import ast
import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

from page_sweep import PAGES, _OPEN_ALL, measure
from visual_check import _THEME_JS, _expected_palettes, launch_chromium

SHOTS = Path(__file__).resolve().parent / "_shots" / "rollout"
SCIENCE = next((SHOTS.parents[2] / "pages").glob("10_*.py"))
CALCULATORS = next(
    ast.literal_eval(node.value) for node in ast.walk(ast.parse(SCIENCE.read_text(encoding="utf-8")))
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "calculators" for t in node.targets)
)
CUSTOM = """() => [...document.querySelectorAll('[data-testid="stMain"] [style]')]
 .filter(e => e.style.fontVariantNumeric === 'tabular-nums' || e.style.display === 'flex')
 .filter(e => {const r=e.getBoundingClientRect();return r.width>0&&r.height>0;})
 .filter(e => e.scrollWidth>e.clientWidth+2)
 .map(e => e.innerText.slice(0,80))"""


def settle(page):
    """Wait for the native running-script control to disappear before QA."""
    page.wait_for_timeout(300)
    page.get_by_role("button", name="Stop", exact=True).wait_for(state="hidden", timeout=60000)
    page.wait_for_timeout(150)


def inspect(page, key, records):
    clipped, overflow = measure(page)
    custom = page.evaluate(CUSTOM)
    errors = page.locator('[data-testid="stException"]').all_text_contents()
    leaked = [text for text in page.locator('[data-testid="stMain"] code').all_text_contents()
              if text.strip() in ("</div>", "</span>")]
    main_overflow = page.locator('[data-testid="stMain"]').evaluate("e => e.scrollWidth-e.clientWidth")
    record = {"view": key, "clipped": clipped, "overflow": overflow,
              "mainOverflow": main_overflow, "customOverflow": custom, "errors": errors, "leakedMarkup": leaked}
    records.append(record)
    assert not errors and not clipped and not custom and not leaked and overflow <= 2 and main_overflow <= 2, record


def run(url, engines):
    SHOTS.mkdir(parents=True, exist_ok=True)
    records, loads, failures = [], [], []
    expected = _expected_palettes()
    with sync_playwright() as p:
        for engine in engines:
            browser = launch_chromium(p)[0] if engine == "chromium" else getattr(p, engine).launch()
            for scheme in ("dark", "light"):
                for width in (1440, 900, 390):
                    context = browser.new_context(viewport={"width": width, "height": 1000}, color_scheme=scheme)
                    page = context.new_page()
                    for route in ["", *PAGES]:
                        key = f"{engine}/{scheme}/{width}/{route or 'Home'}"
                        try:
                            started = time.perf_counter()
                            page.goto(f"{url}/{route}", wait_until="networkidle", timeout=60000)
                            settle(page)
                            if page.get_by_role("dialog").count():
                                page.get_by_role("button", name="Skip", exact=True).click()
                                settle(page)
                            loads.append({"view": key, "seconds": round(time.perf_counter()-started, 3)})
                            actual = page.evaluate(_THEME_JS)
                            assert actual["app"] == expected[scheme]["app"], (key, actual)
                            inspect(page, key+"/initial", records)
                            if engine == "chromium":
                                page.screenshot(path=str(SHOTS / f"{scheme}-{width}-{route or 'Home'}.png"), animations="disabled", timeout=60000)
                            page.evaluate(_OPEN_ALL)
                            inspect(page, key+"/expanded", records)
                            tabs = page.get_by_role("tab")
                            for i in range(tabs.count()):
                                tabs.nth(i).click()
                                page.wait_for_timeout(150)
                                page.evaluate(_OPEN_ALL)
                                inspect(page, key+f"/tab-{i}", records)
                            if route == "Science_Math_Lab":
                                box = page.get_by_role("combobox", name="Select a calculator:")
                                for i, calculator in enumerate(CALCULATORS):
                                    box.click()
                                    box.fill(calculator)
                                    page.get_by_role("option", name=calculator, exact=True).click()
                                    settle(page)
                                    page.evaluate(_OPEN_ALL)
                                    inspect(page, key+f"/calculator-{i}", records)
                                    if engine == "chromium" and width == 390:
                                        page.screenshot(path=str(SHOTS / f"{scheme}-390-calculator-{i}.png"))
                            if route == "Quiz_Assessment":
                                page.get_by_role("button", name="🎯 Start New Quiz", exact=True).click()
                                settle(page)
                                radios = page.get_by_role("radiogroup")
                                assert radios.count() == 10, key
                                for i in range(3):
                                    radios.nth(i).get_by_role("radio").first.press("Space")
                                    settle(page)
                                print(f"Quiz progress {key}: {page.get_by_text('answers selected', exact=False).all_text_contents()}", flush=True)
                                page.get_by_text("3/10 answers selected", exact=True).wait_for(timeout=10000)
                                inspect(page, key+"/quiz-active", records)
                                page.get_by_role("button", name="✅ Submit Quiz", exact=True).click()
                                settle(page)
                                page.get_by_role("button", name="🔁 Try Another Quiz", exact=True).wait_for(timeout=10000)
                                assert all(radios.nth(i).get_by_role("radio").first.is_disabled() for i in range(10)), key
                                inspect(page, key+"/quiz-scored", records)
                            print(f"PASS {key}", flush=True)
                        except Exception as exc:  # noqa: BLE001
                            failures.append({"view": key, "error": str(exc)})
                            print(f"FAIL {key}: {str(exc)[:300]}", flush=True)
                    context.close()
                    print(f"Completed {engine} {scheme} {width}px", flush=True)
            browser.close()
    (SHOTS / "matrix.json").write_text(json.dumps({"records": records, "loads": loads, "failures": failures}, indent=2), encoding="utf-8")
    assert not failures, f"{len(failures)} matrix views failed; see _shots/rollout/matrix.json"
    print(f"Rollout visual matrix passed: {len(loads)} page visits, {len(records)} inspected states")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8501")
    parser.add_argument("--engines", nargs="+", choices=("chromium", "firefox", "webkit"), default=["chromium", "firefox", "webkit"])
    args = parser.parse_args()
    run(args.url.rstrip("/"), args.engines)
