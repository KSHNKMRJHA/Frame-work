"""All-page SignalBench matrix, including tabs and all calculator outputs.

Run only against a disposable app instance: browser visits can award learner XP.
Captures and measurements are ignored runtime artifacts under _shots/rollout.
"""
import argparse
import ast
import json
import time
import traceback
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

from page_sweep import PAGES, _OPEN_ALL, measure
from visual_check import _THEME_JS, _expected_palettes, launch_chromium

SHOTS = Path(__file__).resolve().parent / "_shots" / "rollout"
SCIENCE = next((SHOTS.parents[2] / "pages").glob("10_*.py"))
CALCULATORS = next(
    ast.literal_eval(node.value) for node in ast.walk(ast.parse(SCIENCE.read_text(encoding="utf-8")))
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "calculators" for t in node.targets)
)
CUSTOM = """() => [...document.querySelectorAll('[data-testid="stMain"] [style], [data-testid="stMain"] .katex-display')]
 .filter(e => e.style.fontVariantNumeric === 'tabular-nums' || e.style.display === 'flex' || e.matches('.katex-display'))
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


def check_quiz(page, key, records):
    """Wait for application states across streamed Streamlit rerenders."""
    page.get_by_role("button", name="🎯 Start New Quiz", exact=True).click()
    expect(page.get_by_role("radiogroup")).to_have_count(10, timeout=10000)
    page.get_by_text("0/10 answers selected", exact=True).wait_for(timeout=10000)
    progress = []
    for i in range(3):
        # The native input is transparent; click its visible label. Locators
        # resolve again for each rerender rather than retaining DOM handles.
        page.get_by_role("radiogroup").nth(i).locator("label").first.click()
        page.get_by_text(f"{i+1}/10 answers selected", exact=True).wait_for(timeout=10000)
        expect(page.get_by_role("radio", checked=True)).to_have_count(i+1)
        progress.append(f"{i+1}/10 answers selected")
    inspect(page, key+"/quiz-active", records)
    records[-1]["quizProgress"] = progress
    records[-1]["questionCount"] = page.get_by_role("radiogroup").count()
    page.get_by_role("button", name="✅ Submit Quiz", exact=True).click()
    page.get_by_role("button", name="🔁 Try Another Quiz", exact=True).wait_for(timeout=10000)
    expect(page.get_by_role("radiogroup")).to_have_count(10)
    radios = page.get_by_role("radio")
    assert radios.count() >= 10, (key, "missing answer controls")
    for i in range(radios.count()):
        expect(page.get_by_role("radio").nth(i)).to_be_disabled()
    inspect(page, key+"/quiz-scored", records)
    records[-1]["disabledRadios"] = radios.count()


def run(url, engines, routes=None, schemes=("dark", "light"), widths=(1440, 900, 390), attempts=1):
    SHOTS.mkdir(parents=True, exist_ok=True)
    records, loads, failures = [], [], []
    expected = _expected_palettes()
    with sync_playwright() as p:
        for engine in engines:
            browser = launch_chromium(p)[0] if engine == "chromium" else getattr(p, engine).launch()
            for scheme in schemes:
                for width in widths:
                    context = browser.new_context(viewport={"width": width, "height": 1000}, color_scheme=scheme)
                    page = context.new_page()
                    page_errors = []
                    page.on("pageerror", lambda error: page_errors.append(str(error)))
                    selected_routes = ["", *PAGES] if routes is None else ["" if r == "Home" else r for r in routes]
                    for route in selected_routes * attempts:
                        key = f"{engine}/{scheme}/{width}/{route or 'Home'}"
                        try:
                            page_errors.clear()
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
                                page.locator('[data-testid="stMain"]').evaluate("e => {e.scrollTop=0;}")
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
                                    # Result captures scroll far below the chooser. Return
                                    # before opening its popup so scrolling cannot close it.
                                    page.locator('[data-testid="stMain"]').evaluate("e => {e.scrollTop=0;}")
                                    page.wait_for_timeout(150)
                                    box.click()
                                    box.fill(calculator)
                                    page.get_by_role("option", name=calculator, exact=True).click()
                                    settle(page)
                                    page.evaluate(_OPEN_ALL)
                                    inspect(page, key+f"/calculator-{i}", records)
                                    if engine == "chromium" and width == 390:
                                        page.locator('[data-testid="stMain"]').evaluate("e => {e.scrollTop=0;}")
                                        page.screenshot(path=str(SHOTS / f"{scheme}-390-calculator-{i}.png"))
                                        results = page.locator('[data-testid="stMain"] [style*="tabular-nums"]')
                                        if results.count():
                                            results.first.scroll_into_view_if_needed()
                                            page.screenshot(path=str(SHOTS / f"{scheme}-390-calculator-{i}-results.png"))
                            if route == "Quiz_Assessment":
                                check_quiz(page, key, records)
                            assert not page_errors, (key, page_errors)
                            loads[-1]["totalSeconds"] = round(time.perf_counter()-started, 3)
                            print(f"PASS {key}", flush=True)
                        except Exception as exc:  # noqa: BLE001
                            failures.append({"view": key, "error": str(exc), "traceback": traceback.format_exc()})
                            failure_name = key.replace("/", "-")
                            page.screenshot(path=str(SHOTS / f"{failure_name}-failure.png"))
                            (SHOTS / f"{failure_name}-failure.html").write_text(page.content(), encoding="utf-8")
                            print(f"FAIL {key}: {str(exc)[:300]}", flush=True)
                    context.close()
                    print(f"Completed {engine} {scheme} {width}px", flush=True)
            browser.close()
    report = "matrix.json" if routes is None else f"matrix-{'-'.join(routes)}.json"
    (SHOTS / report).write_text(json.dumps({"records": records, "loads": loads, "failures": failures}, indent=2), encoding="utf-8")
    assert not failures, f"{len(failures)} matrix views failed; see _shots/rollout/{report}"
    print(f"Rollout visual matrix passed: {len(loads)} page visits, {len(records)} inspected states")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8501")
    parser.add_argument("--engines", nargs="+", choices=("chromium", "firefox", "webkit"), default=["chromium", "firefox", "webkit"])
    parser.add_argument("--routes", nargs="+", choices=("Home", *PAGES), help="Limit a diagnostic rerun; omitted runs every page")
    parser.add_argument("--schemes", nargs="+", choices=("dark", "light"), default=["dark", "light"])
    parser.add_argument("--widths", nargs="+", type=int, choices=(1440, 900, 390), default=[1440, 900, 390])
    parser.add_argument("--attempts", type=int, default=1, help="Explicit repetitions; failed attempts remain failures")
    args = parser.parse_args()
    if args.attempts < 1:
        parser.error("--attempts must be positive")
    run(args.url.rstrip("/"), args.engines, args.routes, args.schemes, args.widths, args.attempts)
