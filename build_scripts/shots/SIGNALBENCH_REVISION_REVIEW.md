# SignalBench revision visual evidence

Both themes were inspected at 1440, 900 and 390 px. Existing 13 captures are retained; these 62 captures use a separate revision prefix. Mobile captures close the native sidebar; the frame capture expands the native field-value legend.

## Findings

- Home: a separate compact 12 px version pill, 1 px border; all 12 native navigation links and descriptions render. Cards have 1 px borders, 8 px radii and no shadow.
- CAN: identity chips wrap, key specs stay readable, and conductors stack on mobile. Lower electrical, level, frame, topology and waveform sections were inspected in both themes.
- Figures: active-theme figure and axes backgrounds; explicit title, label, tick, spine, grid, neutral line, legend and annotation colours. Independent Agg figures avoid pyplot registry growth.
- Frame geometry: all five layout/calculation helpers are unchanged; exact patch paths, field labels, positions, font sizes, limits and figure sizes match the starting head across 116 real frames. Diagram collision gate remains 10/10.
- Dense plot text scales down on phones. Frame field names and exact bit counts now also appear in an optional wrapping text legend. Native image fullscreen remains available for detailed waveform inspection.

## Existing content issue found during lower-profile review

CAN electrical bars show 2–3 V and −1/+1 V differential values, whereas its prose and waveform show 1.5–3.5 V. The hardware prose also labels dominant as “Logic high / 1” and recessive as “Logic low / 0”, while the waveform model maps its dominant state to zero. These existing representations need a focused consistency review. Protocol data and waveform rules were preserved in this styling mission.

## Representative contrast

Ratios use relative sRGB luminance; translucent chip fills are composited over the page before measurement. These measurements are not formal WCAG certification.

| Example | Dark | Light |
|---|---:|---:|
| Primary diagram text / canvas | 15.19:1 | 17.06:1 |
| Muted diagram text and Home descriptions / page | 7.30:1 | 7.24:1 |
| Minimum on-field label / five series fills | 5.09:1 | 5.01:1 |
| Version pill label / fill | 5.09:1 | 5.39:1 |
| Category chip / composited tint | 8.33:1 | 4.80:1 |
| Difficulty chip / composited tint | 5.16:1 | 4.62:1 |

Field names, indices, numeric counts, trace names, chip text and conductor directions carry identities alongside colour.

## Capture inventory

| Section | Theme | Width | Capture |
|---|---|---:|---|
| home | dark | 1440 | [signalbench-revision-dark-1440-home.png](signalbench-revision-dark-1440-home.png) |
| home-nav | dark | 1440 | [signalbench-revision-dark-1440-home-nav.png](signalbench-revision-dark-1440-home-nav.png) |
| encyclopedia-top | dark | 1440 | [signalbench-revision-dark-1440-encyclopedia-top.png](signalbench-revision-dark-1440-encyclopedia-top.png) |
| identity-spec | dark | 1440 | [signalbench-revision-dark-1440-identity-spec.png](signalbench-revision-dark-1440-identity-spec.png) |
| electrical | dark | 1440 | [signalbench-revision-dark-1440-electrical.png](signalbench-revision-dark-1440-electrical.png) |
| conductors | dark | 1440 | [signalbench-revision-dark-1440-conductors.png](signalbench-revision-dark-1440-conductors.png) |
| levels | dark | 1440 | [signalbench-revision-dark-1440-levels.png](signalbench-revision-dark-1440-levels.png) |
| frame | dark | 1440 | [signalbench-revision-dark-1440-frame.png](signalbench-revision-dark-1440-frame.png) |
| topology | dark | 1440 | [signalbench-revision-dark-1440-topology.png](signalbench-revision-dark-1440-topology.png) |
| waveform | dark | 1440 | [signalbench-revision-dark-1440-waveform.png](signalbench-revision-dark-1440-waveform.png) |
| home | dark | 900 | [signalbench-revision-dark-900-home.png](signalbench-revision-dark-900-home.png) |
| home-nav | dark | 900 | [signalbench-revision-dark-900-home-nav.png](signalbench-revision-dark-900-home-nav.png) |
| encyclopedia-top | dark | 900 | [signalbench-revision-dark-900-encyclopedia-top.png](signalbench-revision-dark-900-encyclopedia-top.png) |
| identity-spec | dark | 900 | [signalbench-revision-dark-900-identity-spec.png](signalbench-revision-dark-900-identity-spec.png) |
| electrical | dark | 900 | [signalbench-revision-dark-900-electrical.png](signalbench-revision-dark-900-electrical.png) |
| conductors | dark | 900 | [signalbench-revision-dark-900-conductors.png](signalbench-revision-dark-900-conductors.png) |
| levels | dark | 900 | [signalbench-revision-dark-900-levels.png](signalbench-revision-dark-900-levels.png) |
| frame | dark | 900 | [signalbench-revision-dark-900-frame.png](signalbench-revision-dark-900-frame.png) |
| topology | dark | 900 | [signalbench-revision-dark-900-topology.png](signalbench-revision-dark-900-topology.png) |
| waveform | dark | 900 | [signalbench-revision-dark-900-waveform.png](signalbench-revision-dark-900-waveform.png) |
| home | dark | 390 | [signalbench-revision-dark-390-home.png](signalbench-revision-dark-390-home.png) |
| home-nav | dark | 390 | [signalbench-revision-dark-390-home-nav.png](signalbench-revision-dark-390-home-nav.png) |
| encyclopedia-top | dark | 390 | [signalbench-revision-dark-390-encyclopedia-top.png](signalbench-revision-dark-390-encyclopedia-top.png) |
| identity-spec | dark | 390 | [signalbench-revision-dark-390-identity-spec.png](signalbench-revision-dark-390-identity-spec.png) |
| electrical | dark | 390 | [signalbench-revision-dark-390-electrical.png](signalbench-revision-dark-390-electrical.png) |
| conductors | dark | 390 | [signalbench-revision-dark-390-conductors.png](signalbench-revision-dark-390-conductors.png) |
| levels | dark | 390 | [signalbench-revision-dark-390-levels.png](signalbench-revision-dark-390-levels.png) |
| frame | dark | 390 | [signalbench-revision-dark-390-frame.png](signalbench-revision-dark-390-frame.png) |
| topology | dark | 390 | [signalbench-revision-dark-390-topology.png](signalbench-revision-dark-390-topology.png) |
| waveform | dark | 390 | [signalbench-revision-dark-390-waveform.png](signalbench-revision-dark-390-waveform.png) |
| profile-full | dark | 390 | [signalbench-revision-dark-390-profile-full.png](signalbench-revision-dark-390-profile-full.png) |
| home | light | 1440 | [signalbench-revision-light-1440-home.png](signalbench-revision-light-1440-home.png) |
| home-nav | light | 1440 | [signalbench-revision-light-1440-home-nav.png](signalbench-revision-light-1440-home-nav.png) |
| encyclopedia-top | light | 1440 | [signalbench-revision-light-1440-encyclopedia-top.png](signalbench-revision-light-1440-encyclopedia-top.png) |
| identity-spec | light | 1440 | [signalbench-revision-light-1440-identity-spec.png](signalbench-revision-light-1440-identity-spec.png) |
| electrical | light | 1440 | [signalbench-revision-light-1440-electrical.png](signalbench-revision-light-1440-electrical.png) |
| conductors | light | 1440 | [signalbench-revision-light-1440-conductors.png](signalbench-revision-light-1440-conductors.png) |
| levels | light | 1440 | [signalbench-revision-light-1440-levels.png](signalbench-revision-light-1440-levels.png) |
| frame | light | 1440 | [signalbench-revision-light-1440-frame.png](signalbench-revision-light-1440-frame.png) |
| topology | light | 1440 | [signalbench-revision-light-1440-topology.png](signalbench-revision-light-1440-topology.png) |
| waveform | light | 1440 | [signalbench-revision-light-1440-waveform.png](signalbench-revision-light-1440-waveform.png) |
| home | light | 900 | [signalbench-revision-light-900-home.png](signalbench-revision-light-900-home.png) |
| home-nav | light | 900 | [signalbench-revision-light-900-home-nav.png](signalbench-revision-light-900-home-nav.png) |
| encyclopedia-top | light | 900 | [signalbench-revision-light-900-encyclopedia-top.png](signalbench-revision-light-900-encyclopedia-top.png) |
| identity-spec | light | 900 | [signalbench-revision-light-900-identity-spec.png](signalbench-revision-light-900-identity-spec.png) |
| electrical | light | 900 | [signalbench-revision-light-900-electrical.png](signalbench-revision-light-900-electrical.png) |
| conductors | light | 900 | [signalbench-revision-light-900-conductors.png](signalbench-revision-light-900-conductors.png) |
| levels | light | 900 | [signalbench-revision-light-900-levels.png](signalbench-revision-light-900-levels.png) |
| frame | light | 900 | [signalbench-revision-light-900-frame.png](signalbench-revision-light-900-frame.png) |
| topology | light | 900 | [signalbench-revision-light-900-topology.png](signalbench-revision-light-900-topology.png) |
| waveform | light | 900 | [signalbench-revision-light-900-waveform.png](signalbench-revision-light-900-waveform.png) |
| home | light | 390 | [signalbench-revision-light-390-home.png](signalbench-revision-light-390-home.png) |
| home-nav | light | 390 | [signalbench-revision-light-390-home-nav.png](signalbench-revision-light-390-home-nav.png) |
| encyclopedia-top | light | 390 | [signalbench-revision-light-390-encyclopedia-top.png](signalbench-revision-light-390-encyclopedia-top.png) |
| identity-spec | light | 390 | [signalbench-revision-light-390-identity-spec.png](signalbench-revision-light-390-identity-spec.png) |
| electrical | light | 390 | [signalbench-revision-light-390-electrical.png](signalbench-revision-light-390-electrical.png) |
| conductors | light | 390 | [signalbench-revision-light-390-conductors.png](signalbench-revision-light-390-conductors.png) |
| levels | light | 390 | [signalbench-revision-light-390-levels.png](signalbench-revision-light-390-levels.png) |
| frame | light | 390 | [signalbench-revision-light-390-frame.png](signalbench-revision-light-390-frame.png) |
| topology | light | 390 | [signalbench-revision-light-390-topology.png](signalbench-revision-light-390-topology.png) |
| waveform | light | 390 | [signalbench-revision-light-390-waveform.png](signalbench-revision-light-390-waveform.png) |
| profile-full | light | 390 | [signalbench-revision-light-390-profile-full.png](signalbench-revision-light-390-profile-full.png) |

[DOM assertions and computed pill/card styles](signalbench-revision-review.json)

Every captured state passed the zero-exception and no-horizontal-overflow assertions.
