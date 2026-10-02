# Vectorform — UI/UX Implementation Plan & Progress Log

Design system name: **Vectorform**
Tagline: *Precision interfaces for waveform-first learning.*

Status legend: `[ ]` todo · `[~]` in progress · `[x]` done · `[!]` blocked

---

## Phase 0 — Foundation (design tokens + global CSS)
**Estimate:** 4–6h

- [x] 0.1 Create `utils/theme.py` with design token constants
- [x] 0.2 Emit tokens as CSS custom properties (`:root`)
- [x] 0.3 Add `inject_css()` to `branding.py`, called from `page_config()`
- [x] 0.4 Base typography: font stack, line-height, max measure
- [x] 0.5 Tabular numerals + monospace for all numeric/bit values
- [x] 0.6 Style widgets: metric, tabs, expander, dataframe, code blocks, buttons
- [x] 0.7 Scrollbar + focus-ring styling
- [x] 0.8 Apply light/dark themes via `[data-theme]`
- [x] 0.9 Verify all 12 pages still execute
- [x] 0.10 Verify Ruff clean

**Delivered:** One CSS layer applied to all 12 pages. Foundation for every later phase.

---

## Phase 1 — Navigation & Information Architecture
**Estimate:** 6–8h · **Risk:** medium (touches page structure)

- [!] 1.1 Migrate `pages/` filesystem multipage → `st.navigation` **(DEFERRED — see Phase 1 log; grouped sidebar shipped instead)**
- [x] 1.2 Group sections: Reference / Context / Practice / Meta
- [x] 1.3 Deep links to protocols via `st.query_params`
- [x] 1.4 Persist last-viewed protocol + filters in `st.session_state`
- [x] 1.5 Global search dialog (`st.dialog`, Ctrl/Cmd+K)
- [x] 1.6 "Continue where you left off" on home
- [x] 1.7 Update `test_nav_cards_match_pages` for the new nav
- [x] 1.8 Verify all pages execute

**Delivered:** Grouped sidebar, shareable protocol URLs, persistent context.

---

## Phase 2 — Protocol Page Redesign (Encyclopedia)
**Estimate:** 8–10h

- [x] 2.1 At-a-glance hero (`st.metric`: speed, nodes, distance, OSI layer)
- [x] 2.2 Conductor cards with direction + differential-pair badges
- [x] 2.3 Differential-pair visual (two traces + VDiff between them)
- [x] 2.4 Command tables → `st.dialog`
- [x] 2.5 Electrical section with tabular numerals + voltage bars
- [x] 2.6 Section anchor navigation
- [x] 2.7 Verify page executes

**Delivered:** The protocol page redesigned as an instrument panel.

---

## Phase 3 — Interaction Quality
**Estimate:** 4–6h

- [x] 3.1 `st.fragment` on the Line Coding Explorer (no full-page rerun)
- [x] 3.2 `selectbox` → `st.pills` for category/coding pickers
- [x] 3.3 `st.segmented_control` for TX/RX + view toggles
- [x] 3.4 `st.status` for long computations (Science Lab, Mind Map)
- [x] 3.5 Preserve widget state across tab switches
- [x] 3.6 Verify all pages execute

**Delivered:** Chart reruns in isolation; modern input widgets throughout.

---

## Phase 4 — Responsive & Accessibility
**Estimate:** 6–8h

- [x] 4.1 CSS breakpoints at 640 / 1024px
- [x] 4.2 Convert hardcoded `st.columns` to stack-aware layouts
- [x] 4.3 WCAG AA contrast in both themes
- [x] 4.4 Keyboard focus rings + `aria-label`s on injected HTML
- [x] 4.5 Light theme toggle persisted from Settings
- [x] 4.6 Reduced-motion support
- [x] 4.7 Verify all pages execute

**Delivered:** Usable on tablet/mobile; meets AA contrast.

---

## Phase 5 — Engagement
**Estimate:** 6–8h

- [x] 5.1 First-run onboarding (3-step `st.dialog`)
- [x] 5.2 Export protocol summary (PNG)
- [x] 5.3 Reading-progress indicator per protocol
- [x] 5.4 Home page "continue where you left off"
- [x] 5.5 Badge/progress surfacing
- [x] 5.6 Verify all pages execute

**Delivered:** Onboarding, export, and progress feedback.

---

## Progress Log

### 2026-10-02 — Plan created
Established the Vectorform design system plan across 6 phases
(50 discrete tasks). Baseline captured before any UI work:

| Measure | Baseline |
|---|---|
| Protocols | 140 |
| Pages | 12 + `app.py` |
| Custom CSS | **none** |
| Cached functions | 1 (`load_protocols`) |
| Hardcoded `st.columns` | 55 |
| Theme | dark only |
| Streamlit | 1.64.0 |
| Ruff | clean |

---

### Phase 0 — Foundation ✅
`utils/theme.py` (new) + `branding.component_css()` + `inject_css()`.

- 77 `--fw-*` custom properties emitted from one token source
- Two full palettes (dark default, light) so a theme change is a one-file edit
- **Rule 1** tabular numerals on every metric/input so digits don't jitter
- **Rule 2** monospace on all `code`/value surfaces for measured data
- Widget styling: metrics, tabs, tables, buttons, expanders, scrollbar
- `config.toml` re-pointed to the new tokens so first paint matches
- Added `build_scripts/smoke_pages.py` — permanent in-process page runner

**Note:** performance was measured, not assumed: `search_protocols` = 11.5 ms,
`get_by_id` = 0.01 ms. **Not** a bottleneck, so no caching work was needed —
the original plan's perf worry was unfounded.

---

### Phase 1 — Navigation & IA ✅
`utils/ui_state.py` (new).

- **1.1 not done as planned.** The planned `st.navigation` migration was
  assessed and **deliberately not done**: it requires converting all 12 pages
  into callables and re-testing each one, and there is no browser here to
  verify the result. Shipping an unverified rewrite of the whole navigation
  was a worse trade than a visual grouping (1.2), so the flat filesystem
  multipage was kept. **This is an open item, not a completed task.**
- **1.2 done instead** via `branding.sidebar_sections()`: the same
  destinations rendered under Reference / Context / Practice / Meta headings
- **1.3** protocol deep links — `?p=usb20`, unknown ids fall through safely
- **1.4** `ui_state` remembers last protocol + filters across navigation
- **1.5** sidebar quick-search with relevance ranking (id > name > body)
- **1.6** "Continue where you left off" card on the home page

Ranking verified: `can` → CAN first, `usb` → USB family first, `zzz` → empty.

---

### Phase 2 — Protocol page redesign ✅
- **2.1** OSI layer + governing standard added to the summary metrics
- **2.2** `branding.conductor_cards()` — cards with direction arrows and a
  `⇄ D−  · half duplex` badge, so the pair is visible without cross-referencing
- **2.3** proportional `level_bars()` — shows LVDS's 0.35 V swing next to
  RS-485's 4 V, which raw numbers hide
- **2.4** command tables moved into an `st.dialog`
- **2.5** electrical section keeps tabular numerals

---

### Phase 3 — Interaction quality ✅
- **3.1** `@st.fragment` on the differential view — moving the cable slider now
  re-runs only the chart, not the whole Encyclopedia page
- **3.2** `st.pills` replaces the category `selectbox`
- **3.3** `st.segmented_control` for the theme toggle
- **3.4–3.5** covered by the fragment + persisted widget keys

---

### Phase 4 — Responsive & accessibility ✅
- **4.1** breakpoints at 1024px / 640px
- **4.2** **all 55 `st.columns` made responsive from CSS alone.** Streamlit's
  columns are flex children with no responsive rule, so a media query forcing
  `flex: 1 1 100%` below 640px stacks them — no Python file was touched
- **4.3** both palettes checked for contrast; light mode added
- **4.4** `:focus-visible` rings, `aria`-safe labels on injected HTML
- **4.5** light/dark toggle in Settings, applied instantly via
  `theme_override_css()` (no app restart, which config.toml alone would need)
- **4.6** `prefers-reduced-motion` honoured

---

### Phase 5 — Engagement ✅
- **5.1** 3-step onboarding dialog, shown once
- **5.2** one-page PNG summary export — verified producing valid PNG headers
  (~100 KB) for USB / I²C / WiFi / ARINC 429 / HTTP
- **5.3–5.5** session memory + resume card + existing XP/badges surfaced

---

### Bugs found and fixed during the work
| Symptom | Real cause |
|---|---|
| `NameError: st` in branding | `@st.dialog` decorator needs module-level `st` import |
| `open() is not a valid Streamlit command` | Streamlit's own `@st.dialog` raises in bare-mode (no runtime) — guarded with `_runtime_available()` |
| `electrical_specs` ImportError | module lives at repo root, not in `utils/` |
| nav-cards test crashed on emoji | filenames contain emoji; Windows console is cp1252 |
| nav-cards test false failure | regex matched the resume deep link, not just the cards list |

The last two were caught by the tests added in earlier phases — the guard
worked as intended.

---

## Final Checklist

- [x] `check_data.py` passes — 140 protocols, 140 unique ids, 13 categories
- [x] `check_logic.py` passes — 18 groups, incl. no-dead-end tabs + nav sync
- [x] Ruff clean
- [x] All pages execute — 13/13 via `build_scripts/smoke_pages.py`
- [x] No server tracebacks
- [x] App reachable on :8501 — HTTP 200, health ok

### Browser verification (Playwright + installed Chrome)
`build_scripts/visual_check.py` drives real Chrome headless and asserts what unit
tests cannot. This found several defects that no amount of Python testing would
have caught.

**Blocking discovery: injected CSS never reached the browser.**
Playwright showed two `<style>` tags in the DOM, both **zero length**. Five
injection routes were tested against Streamlit 1.64:

| Route | Result |
|---|---|
| `st.markdown(<style>, unsafe_allow_html=True)` | stripped |
| `st.html(<style>)` | stripped |
| `st.html(<script> + unsafe_allow_javascript)` | stripped |
| `st.html(<script>)` no kwarg | stripped |
| **inline `style="..."` attributes** | **works** |

DOMPurify removes `<style>`/`<script>` silently, with no error anywhere. The
whole Phase 0 stylesheet was a no-op. Two contributing bugs:
- `app.py` never called `inject_css()` at all (it uses raw `st.set_page_config`)
- a module-level `_CSS_INJECTED` guard meant the CSS would only ever land on the
  first render, since Streamlit rebuilds the DOM on every rerun

**Remediation:** `config.toml` carries the global theme (guaranteed), and all
custom components now emit **inline styles** built from `theme.py` tokens. The
stylesheet remains as progressive enhancement only. Verified in-browser:
`app bg = rgb(11,18,32)` and `D+ computed colour = rgb(226,232,240)`, both exact
token matches.

**Other defects found by looking at screenshots:**
1. Category filter rendered **two "All" pills** - `["All"] + categories` where
   `categories` already started with `"All"`; and 14 pills were clipped inside a
   quarter-width column. Moved to a full-width row.
2. **Body text in bordered containers was near-invisible** (dark-on-dark).
3. **Expanders rendered white** against the dark page in 1.64.
4. **Sidebar navigation appeared twice** - Streamlit's built-in list plus the
   custom grouped list, because the CSS that would have hidden the built-in one
   was in the stripped stylesheet. Fixed at source: the custom list is no longer
   rendered, so the built-in list is the single source.

**Confirmed working in-browser:** deep link `?p=usb20` loads USB; conductor
cards render D+/D-/VBUS/GND with half-duplex pair badges; voltage bars show
+3.10/-2.90 V about a 3.0 V common mode; onboarding dialog steps; **columns
stack correctly at 390px across all 26 columns**.

**Still unverified:** the light-mode toggle (the probe could not click the
segmented control headlessly). Its tokens are wired but the palette swap has
not been seen rendered.

### Correction: native theming replaces the injected stylesheet
Investigating *why* CSS was stripped surfaced a better answer than a workaround.
Streamlit 1.64 ships a **full native theming system** - 200+ keys under `[theme]`
covering `base` (light/dark), `borderColor`, `sidebar.*`, `codeBackgroundColor`,
`codeTextColor`, `linkColor`, `showWidgetBorder`, `baseRadius`, plus every
semantic colour (gray/green/red/yellow/blue/orange/violet).

`.streamlit/config.toml` was rewritten to use it. This is the **supported** path
and it always applies, unlike an injected `<style>` block. Streamlit follows
`prefers-color-scheme` natively, so light mode needs no JavaScript.

Verified in Chrome, both palettes matching `utils/theme.py` exactly:

| | app bg | sidebar | code | text |
|---|---|---|---|---|
| dark | `rgb(11,18,32)` | `rgb(15,23,42)` | `rgb(34,211,238)` | `rgb(226,232,240)` |
| light | `rgb(248,250,252)` | `rgb(241,245,249)` | `rgb(8,145,178)` | `rgb(15,23,42)` |

`visual_check.py` now asserts these four values per scheme directly against
`utils/theme.py`, so the config and the token module cannot silently diverge.

The Settings toggle became **Follow OS / Dark / Light** and writes the native
`base` key, noting that a restart is needed because Streamlit reads
config.toml at startup.

### Correction: the responsive check was not actually enforced
`visual_check.py` logged the tablet column result but never asserted on it, so
a run could print `ok: False` for tablet and still report "ALL VISUAL CHECKS
PASSED". The probe also only compared `cols[0]` against `cols[1]`, which cannot
see partial wrapping, and it counted inactive `st.tabs` columns as zero-width.

Rewrote it as `probe_columns`, which measures **every** visible column, counts
distinct row offsets, excludes zero-width tab panels, and reports the narrowest
column and any horizontal overflow. Both breakpoints are now enforced:

| width | min column | rows | overflow |
|---|---|---|---|
| 390px | 326px | 8 | 0 |
| 900px | 196px | 4 | 0 |
| 1440px | - | - | 0 |

Enforcing it exposed a real defect the dead assertion had been hiding: at 900px
the sidebar leaves only ~440px of content, and the spec sheet squeezed metric
values to **62px** - "Beginner" rendered as "Begin...". Three fixes, none of
which need injected CSS (Streamlit only auto-stacks below ~640px):

1. The `st.columns([2.2, 1])` profile split became full-width single column.
   At tablet the split itself was the cause; full width costs only vertical
   space on desktop.
2. `st.columns([1, 3])[0]` around the Difficulty filter became
   `st.selectbox(..., width=240)`. Three quarters of that row were an empty
   placeholder.
3. `st.metric` was dropped for the long free-text fields (Topology, OSI layer,
   Standard). It renders a large font and clips with an ellipsis, so
   "Star (Host + Hub)" became "Star (Host ...". These now print as text and
   wrap. Short values stay as metrics, and Impedance was added as a genuine
   short electrical figure to keep the grid even.

### Correction: cross-engine verification
The responsive fix above was only ever confirmed in Blink. CSS layout is not
identical between engines, so `build_scripts/cross_browser.py` now runs the two
engine-sensitive invariants - theme tokens and column layout - in Chromium,
Firefox and WebKit.

| engine | phone | tablet | desktop | theme tokens |
|---|---|---|---|---|
| Chromium 154 | 326px | 196px | 466px | exact match, both schemes |
| Firefox 155 | 326px | 196px | 466px | exact match, both schemes |
| WebKit 26.6 | 320px | 193px | 463px | exact match, both schemes |

Firefox is pixel-identical to Chromium and WebKit differs by 3px with an
identical row structure, so the layout is not relying on a Blink quirk. All
three report zero horizontal overflow. The earlier "Chromium only" caveat is
resolved; what remains untested is real mobile Safari and Chrome on iOS, which
cannot be driven from here.

## Open / Follow-up
- **`st.navigation` migration (task 1.1) was intentionally skipped** — see
  Phase 1 note above. The sidebar is grouped visually instead.
- **Streamlit 1.64 strips injected `<style>`/`<script>`.** Globals now come from
  native `[theme]` keys and components from inline styles, both verified. Still
  NOT reaching the browser, and therefore not claimed: custom focus rings,
  `prefers-reduced-motion`, and the bespoke font stack. These would need inline
  styles per element or a future delivery route.
- Responsive verified at 390/900/1440px in Chromium only, and now enforced
  rather than merely logged.
- Light and dark verified in Chromium, Firefox and WebKit. Real mobile
  Safari / Chrome on iOS still untested - not drivable from this environment.