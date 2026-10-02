# Independent verification report — plant disease monitor

## V.0 Metadata

**Agent/date:** independent verification agent; 2026-09-26 (Asia/Kolkata).

**Artifacts verified**

| Artifact | Evidence identity |
|---|---|
| Project plan | `C:\Users\Lenovo\Documents\Codex\2026-09-25\i\outputs\plant-disease-project-plan.md`; 40,743 bytes; SHA-256 `EF1D48AC2D26800DFE4A8EBC2506F0FD82CA0DC78822E27CEB5C1EE55A9FC80E` |
| Airtime/battery calculator | `C:\Users\Lenovo\.codex\visualizations\2026\09\25\01a0d9ab-36cd-7e13-8498-730a38fd1cdd\plant-lora-budget.html`; 7,795 bytes; SHA-256 `73E1B65CA265790B082E38DBD85B556F5278F0CF4B86DD0B0777BAE299126267` |
| Implementation repository | `C:\Users\Lenovo\.cline\worktrees\641bc\empromy`; HEAD `d3a9db3c480b7e7f625ee83669c90dc8660641f1`; branch `cline/641bc` |

The repository is present and writable, but its files are an unrelated Python/Streamlit/Kivy educational application. `git status --short --branch` reports many pre-existing modified and untracked files. No firmware, gateway, protocol, model, dataset manifest, RF log, serial log, `specs/`, `prisma/`, `api-contract.md`, partition CSV, `sdkconfig*`, Rust/Go/Zig/TypeScript source, or dependency lockfile was found. Only `requirements.txt` was found as a dependency manifest. This report is the only new file created.

Evidence was checked against primary sources, including the [ESP32-S3-WROOM-1 datasheet](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf), [ESP32-S3 GPIO documentation](https://docs.espressif.com/projects/esp-idf/en/v5.0/esp32s3/api-reference/peripherals/gpio.html), [ESP32-S3 hardware design checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html), [official camera driver](https://github.com/espressif/esp32-camera), [Semtech SX1262 product/datasheet page](https://www.semtech.com/products/wireless-rf/lora-connect/sx1262), [India G.S.R. 853(E) Gazette](https://egazette.gov.in/WriteReadData/2021/231828.pdf), [DoT ETA page](https://www.eservices.dot.gov.in/equipment-type-approval-eta), [ESP-IDF partition documentation](https://docs.espressif.com/projects/esp-idf/en/v5.0/esp32/api-guides/partition-tables.html), [ESP-IDF OTA documentation](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/system/ota.html), [TI BQ24074](https://www.ti.com/product/BQ24074), [TI TPS63070](https://www.ti.com/product/TPS63070), [PlantVillage card](https://huggingface.co/datasets/mohanty/PlantVillage), [PlantDoc repository](https://github.com/pratikkayal/PlantDoc-Dataset), [Rice dataset](https://data.mendeley.com/datasets/fwcj7stb8r/2), [LiteRT Linux/Pi documentation](https://developers.google.com/edge/litert/microcontrollers/python), and [Mojo requirements](https://mojolang.org/docs/requirements/).

## V.1 Executive verdict

**PLAN NEEDS CHANGES.** The plan is a useful design hypothesis and correctly labels many values as estimates, but it is not an implementation and cannot be called verified. Three blockers are independently reproducible:

1. The supplied calculator does not parse. Node reports `SyntaxError: missing ) after argument list` at the `payloadSymbols` expression in HTML line 58, so none of its controls or results execute.
2. The proposed first 64 KiB flash region is not a valid ESP-IDF partition table. It combines bootloader, partition table, NVS, OTA metadata and PHY without the required explicit `otadata`/partition entries. The plan itself calls this a concept, but the verification brief requires a valid table before accepting OTA claims.
3. There is no code or hardware evidence for GPIO assignment, RF module/antenna approval, raw-LoRa airtime scheduling, security counters, camera quality, LiteRT deployment, battery sleep current, or field accuracy. The 3–5 km and 8 KiB diagnostic claims therefore remain engineering hypotheses.

The arithmetic for fragments, LoRa time-on-air, storage, Fresnel radius, and the stated battery model reproduces when the plan's assumptions are used. Those are `[CE]`, not measured field results. Raw LoRa is a private single-radio link; LoRaWAN regional parameters do not by themselves establish the Indian legal classification or duty-cycle permission.

## V.2 Results table

Labels: `[DS]` datasheet/primary source; `[M]` measured in this verification; `[EA]` engineering assumption; `[CE]` calculated estimate. `Y` means a hardware, field, or implementation test is required to close the finding.

### V1 — Hardware

| ID | Claim | Verdict | Evidence (quote/command/URL) | Confidence | Impact | Required correction | Test? |
|---|---|---|---|---|---|---|---|
| HW-01 | N16R8 memory and thermal rating | CONFIRMED | `[DS]` WROOM-1 datasheet table identifies N16R8 as 16 MB Quad flash and 8 MB Octal PSRAM. The same table/notes state the normal ambient range and that ECC permits 85 °C with one-sixteenth usable PSRAM reduction. | High | Memory and enclosure design are plausible. | Record exact module marking and verify ECC mode in `sdkconfig`; measure enclosure temperature. | Y |
| HW-02 | GPIO35/36/37 unavailable with octal memory | CONFIRMED | `[DS]` ESP-IDF GPIO documentation says GPIO35/36/37 are unavailable when octal flash/PSRAM is used; the hardware guide reserves those memory pins. | High | A pin map using any of these pins would fail. | Publish the exact carrier schematic and pin map. | Y |
| HW-03 | OV2640/JPEG/PSRAM camera path | CONFIRMED (capability only) | `[DS]` [esp32-camera README](https://github.com/espressif/esp32-camera) supports ESP32-S3 and OV2640; larger JPEG frames require PSRAM, and the driver documents JPEG quality and XCLK configuration. No selected camera board or capture log exists. | High for driver capability; low for system | Camera board voltage, pinout, buffer ownership and image-size distribution remain open. | Name the exact camera board, driver commit and capture configuration; attach logs. | Y |
| HW-04 | Approximately 25 direct MCU signals | UNVERIFIABLE | `[EA]` Plan line 118 counts the signals but supplies no GPIO numbers. The GPIO guide reserves octal-memory pins and several pins have strapping/USB/JTAG constraints. | High | The proposed camera, SD, radio and service interfaces may not fit the chosen board. | Produce a board-specific schematic with every GPIO, boot state, voltage and alternate function. | Y |
| HW-05 | SX1262 pins, RF switch/TCXO, 255-byte payload and SPI timing | UNVERIFIABLE | `[DS]` Semtech product page confirms SX1262 features and +22 dBm class. The plan gives no named module or datasheet pin routing, no SPI clock, and no DIO2/DIO3 configuration proof. | Medium | Wrong TCXO/RF-switch wiring or an over-clocked shared bus can make the radio fail. | Select a module and attach its schematic plus the SX1262 datasheet timing limits; choose the shared SPI clock from the minimum limit. | Y |
| HW-06 | 862–930 MHz module with TCXO | UNSUPPORTED | `[EA]` Plan says “matched for 865–868 MHz” but BOM has no manufacturer/part number. | High | RF approval, oscillator start-up and conducted-power claims cannot be reproduced. | Freeze a module with frequency range, TCXO, DIO2/DIO3 routing, antenna connector and India approval evidence. | Y |
| HW-07 | I²C addresses and pull-up budget | UNVERIFIABLE | `[DS]` SHT40 vendor page supports I²C; plan names SHT40, BH1750, ADS1115 and MCP23017 but does not state actual addresses, pull-ups or powered-off leakage. | High | Address collision or excessive parallel pull-up current can break the bus or sleep budget. | Attach schematics/datasheets and calculate effective pull-up resistance at every power state. | Y |
| HW-08 | BQ24074 solar power path | CONFIRMED (device facts); UNSUPPORTED (system selection) | `[DS]` TI lists 1-cell, 1.5 A, 4.35 V minimum input, 10.2 V operating maximum, 28 V absolute maximum, power path and 4.2 V battery. The plan correctly warns that its output is unregulated. | High | A 6 V panel may work, but panel Vmp, thermal headroom and system rail are not proven. | Choose the exact charger board, NTC, input protection and measured charge profile. | Y |
| HW-09 | TPS63070 regulator | CONFIRMED (device facts); UNSUPPORTED (module implementation) | `[DS]` TI product page states 2–16 V input, up to 2 A buck/boost output and 50 µA typical quiescent current; the plan has no selected module or temperature/current data. | High for facts | Converter efficiency and transient performance dominate node power. | Identify part/package and measure efficiency, Iq and load transients. | Y |
| HW-10 | Pi 5 27 W supply/thermal assumptions | UNVERIFIABLE | `[DS]` Raspberry Pi product documentation specifies the official supply capability and active cooling guidance; the plan's 8 W gateway load and idle/stress values are `[EA]`, not measurements. | High | Gateway battery and panel sizing may be wrong. | Measure the complete gateway at idle, receive, inference and storage workloads. | Y |
| HW-11 | Shared SPI bus | UNVERIFIABLE | Plan §4 says SX1262 and microSD share SCK/MOSI/MISO, but no clock or CS sequencing is implemented. | High | SD and radio transactions can corrupt each other. | State the clock as the minimum of the selected radio/module and SD limits; add lock/CS/tri-state tests. | Y |
| HW-12 | ESP32 power/ESD guidelines | CONFIRMED (guideline) | `[DS]` Espressif checklist requires a 3.3 V supply able to deliver at least 500 mA, at least 10 µF at the power entrance and ESD/power protection considerations. | High | This is a sound schematic requirement, not proof of the carrier. | Show schematic and brownout test. | Y |

### V2 — India RF compliance (raw LoRa, 865–868 MHz)

| ID | Claim | Verdict | Evidence | Confidence | Impact | Required correction | Test? |
|---|---|---|---|---|---|---|---|
| RF-01 | Rule identity | CONFIRMED | `[DS]` The official Gazette PDF title is “Use of Low Power Equipment in the Frequency Band 865–868 MHz for Short Range Devices (Exemption from Licence) Rules, 2021”; it is dated 10 Dec 2021. | High | Correct source identified. | Keep the Gazette revision in the compliance folder. | N |
| RF-02 | Table II conditions | CONFIRMED | `[DS]` Gazette Table II lists Tracking, Tracing and Data Acquisition Devices: 500 mW ERP, APC, occupied bandwidth ≤200 kHz, 10% duty for network access points and 2.5% otherwise, with EN 300 220 conditions. | High | These limits are usable only if WPC accepts this classification. | Obtain written classification/ETA for the actual product. | Y |
| RF-03 | Table I versus Table II | UNSUPPORTED | `[DS]` The same Gazette Table I gives non-specific SRD 25 mW ERP and a different duty rule. The plan calls Table II “provisional” but supplies no product classification argument. | High | Applying the 2.5%/500 mW row without classification could be non-compliant. | Document the device function, category, APC implementation, emission bandwidth and WPC classification before field transmission. | Y |
| RF-04 | ERP arithmetic | CONFIRMED (conditional) | `[CE]` +22 dBm conducted +2 dBi = 24 dBm EIRP; ERP = EIRP−2.15 = 21.85 dBm = 153 mW. +22 dBm +5 dBi = 27 dBm EIRP = 24.85 dBm ERP = 306 mW, before cable loss. | High | Values fit the 500 mW ceiling, but antenna/cable and classification remain required. | Measure conducted power and antenna/cable loss; record ERP. | Y |
| RF-05 | ETA requirement/self-declaration | CONFIRMED (general requirement) | `[DS]` DoT says ETA is required for import, sale and use of wireless devices in de-licensed/RF bands and permits self-declaration for eligible SRDs; the page lists RF test report, manufacturer authorization and technical literature. | High | A module alone is not the project ETA. | Obtain ETA or documented applicability determination for the finished radio product. | Y |
| RF-06 | Fresnel radii | CONFIRMED | `[CE]` At 866 MHz, λ=0.3462 m; midpoint r₁ is 16.1 m at 3 km and 20.8 m at 5 km; 60% is 9.7/12.5 m. | High | Mast heights must be checked against terrain/crop height. | Survey the actual path and measure clearance. | Y |
| RF-07 | 2–5 km range/RSSI | UNSUPPORTED | `[CE]` FSPL is 91.19 dB (1 km), 97.21 dB (2 km), 100.73 dB (3 km), 105.17 dB (5 km). With +22 dBm, 2 dBi node, 5 dBi gateway and no cable loss, received power is −71.73 dBm at 3 km and −76.17 dBm at 5 km. This is not the plan's unexplained −74/−78 dBm and does not include foliage, Fresnel loss, polarization, receiver sensitivity or interference. | High | A nominal link budget is not a delivery guarantee. | Run a path survey and packet test with mature/wet crop; use the selected module's measured sensitivity (SF9 is not established by the cited product summary). | Y |
| RF-08 | Airtime legality and daily caps | UNSUPPORTED | `[CE]` 2.5% gives 2,160 s/day. With 20% retry allowance, an 8 KiB image permits 36/20/9/5 images/day at SF9/10/11/12 respectively. That ceiling applies only after Table II classification and must include all node and applicable downlink transmissions. | High | “8 KiB hourly legal” is conditional at SF9 and false at SF10+ under the stated cap. | Implement a rolling ledger for image, telemetry, ACK and retries; get WPC classification. | Y |

### V3 — Protocol and airtime

| ID | Claim | Verdict | Evidence | Confidence | Impact | Required correction | Test? |
|---|---|---|---|---|---|---|---|
| PT-01 | 240-byte payload | CONFIRMED (arithmetic) | `[CE]` 24-byte header + 200-byte content + 16-byte tag = 240 bytes, below the SX1262 explicit payload maximum stated by the selected modem configuration. | Medium | Byte order and actual modem setting are still absent. | Add a versioned protocol document and test vectors. | Y |
| PT-02 | Fragment counts | CONFIRMED | `[CE]` `ceil(size×1024/200)` gives 21, 41, 62 and 103 fragments for 4, 8, 12 and 20 KiB. | High | None if the declared length and final short fragment are enforced. | Add unit tests for boundary sizes. | Y |
| PT-03 | ToA table | CONFIRMED | `[CE]` Formula with BW=125 kHz, CR=4/5, explicit header, CRC, preamble 8 and LDRO SF11/12 gives SF7 0.379136 s, SF9 1.188864 s, SF10 2.172928 s, SF11 4.755456 s, SF12 8.527872 s for 240 bytes. | High | Arithmetic is sound; modem register settings must match. | Put formula and test vectors in code. | Y |
| PT-04 | Retry/ACK/downlink | PARTLY CONFIRMED | `[CE]` A 48-byte ACK is 0.308224 s at SF9 and 2.301952 s at SF12; six ACKs for 41 fragments are 1.849344 s at SF9. The plan does not define a 48-byte ACK schema or prove that six downlinks fit its ledger. | High | Channel occupancy and gateway energy are undercounted if ACKs are omitted. | Specify ACK bytes/window and count node plus gateway airtime separately. | Y |
| PT-05 | SF9 hourly airtime | PARTLY CONFIRMED | `[CE]` 41×1.188864×1.2 = 58.4921 s image airtime; adding the plan's 6.5 s/hour scaled telemetry gives about 64.99 s/hour. Six ACKs add about 1.85 s gateway airtime. | High | The 58.5 s node figure is correct; the ~63.5 s total is not a complete channel total. | Include ACKs, receive windows, competing nodes and retries in the ledger. | Y |
| PT-06 | SF12 pacing | CONFIRMED (estimate) | `[CE]` 41×8.527872×1.2 = 419.5713 s; 419.57/90 = 4.66 h average at the proposed 90 s/hour cap. | High | Average pacing is not a guarantee under a rolling/legal duty window. | Implement and test a rolling window scheduler. | Y |
| PT-07 | Resume state | UNSUPPORTED | Plan §6 describes manifests/bitmaps, but repository inventory found no firmware, gateway journal, checksum or fsync code. | High | A reset can duplicate or lose a multi-hour image. | Implement persistent node/gateway state and restart tests. | Y |
| PT-08 | AEAD nonce/counter design | UNSUPPORTED | Plan line 150 proposes AES-128-CCM and a 13-byte nonce, but no mbedTLS calls, HKDF/key provisioning, counter persistence or dedupe code exists. | High | Replay or nonce reuse could compromise commands/images. | Provide reviewed crypto code, test vectors, encrypted NVS/eFuse provisioning and replay tests. | Y |
| PT-09 | LoRa OTA cost | CONFIRMED (estimate) | `[CE]` 3 MiB at 200 bytes/fragment is 15,729 fragments; at SF9 that is 5.194 h raw and 6.233 h with 20% retry, before ACK/control overhead. | High | Correctly excluded from the baseline. | Keep LoRa OTA disabled unless a separate duty/downlink design is approved. | N |
| PT-10 | Calculator consistency | INCORRECT | `[M]` Extracting the script to a scratch file and running `node --check` reports `SyntaxError: missing ) after argument list` at source line 10 (HTML line 58): `const payloadSymbols = 8 + Math.max(...`. The local-file browser load was blocked by browser URL policy, so interactive control exercise was not possible; the parse error already prevents rendering. | High | All calculator outputs are non-functional until fixed. | Add the missing `)` (and then browser-test every control against independent vectors); do not treat static labels as computed results. | Y |

### V4 — Image quality and computer vision

| ID | Claim | Verdict | Evidence | Confidence | Impact | Required correction | Test? |
|---|---|---|---|---|---|---|---|
| CV-01 | 4–8 KiB preserves diagnosis | UNVERIFIABLE | Plan explicitly says an 8 KiB image may preserve too little detail (line 26) and contains no acceptance data. | High | The central bandwidth decision is unproven. | Run the specified paired-size field study before freezing the protocol. | Y |
| CV-02 | Capture settings | CONFIRMED (design/source) | `[DS]` Official esp32-camera documentation supports JPEG, PSRAM and ESP32-S3; plan specifies VGA capture then PSRAM resize/re-encode. No implementation exists. | High for design; low for execution | Re-encode time and quality may invalidate power assumptions. | Measure one-frame buffer ownership, time, current and resulting byte distribution. | Y |
| CV-03 | Compression acceptance test | UNSUPPORTED | Plan lists compression study as a schedule task, but no test, dataset, metrics or results exist. | High | No evidence supports 8 KiB. | Test ≥100 healthy/diseased field images, 4/8/12/20 KiB variants, macro-F1, per-class recall, confidence and rejection rate. | Y |
| CV-04 | Image quality gate | UNSUPPORTED | Plan names blur/darkness/overexposure/tiny-leaf/obstruction gates but repository has no implementation. | High | Bad images consume scarce airtime and create false alerts. | Implement or explicitly defer the gate and measure false rejection/acceptance. | Y |
| CV-05 | MobileNetV3/INT8/calibration | UNSUPPORTED | Plan states MobileNetV3-Small, INT8, representative compressed images and calibration, but no model, calibration set, FP32 comparison or temperature-scaling artifact exists. | High | Accuracy/latency claims are not reproducible. | Pin model/runtime versions and publish model package, calibration manifest, thresholds and held-out metrics. | Y |

### V5 — Datasets and licensing

| ID | Claim | Verdict | Evidence | Confidence | Impact | Required correction | Test? |
|---|---|---|---|---|---|---|---|
| DS-01 | PlantVillage | CONFIRMED (with legal caveat) | `[DS]` Dataset card reports 54,306 images, 14 crop species and 26 diseases and declares CC BY-SA 3.0. Share-alike obligations must be reviewed before distributing commercial weights. | High | Controlled imagery may not represent Indian field conditions. | Preserve attribution and legal review; add field data. | Y |
| DS-02 | PlantDoc | CONFIRMED | `[DS]` Authors' paper reports 2,598 images, 13 species and up to 17 disease classes; repository includes CC-BY-4.0 licensing. | High | Label quality and duplicates still need audit. | Store a manifest and split by plant/plot/date. | Y |
| DS-03 | Rice dataset | CONFIRMED (healthy gap remains) | `[DS]` Mendeley v2 reports 5,932 images, four named diseases and CC BY 4.0. The page does not provide a healthy class in the cited description. | High | A disease-only dataset cannot calibrate healthy/uncertain rejection. | Add healthy, nutrient/water stress and wrong-crop examples. | Y |
| DS-04 | Chilli/cotton gaps | CONFIRMED (gap); dataset availability UNVERIFIABLE | Plan correctly says chilli and cotton need separate labelled data; no licence-cleared Indian chilli/cotton manifest is in the artifacts. | High | One universal model would be misleading. | Obtain agronomist-reviewed, licence-recorded data or keep those crops out of launch. | Y |
| DS-05 | One crop/one model first | CONFIRMED (plan decision) | Plan chooses tomato first and separates potato, chilli, rice and cotton plans. | High | Reasonable scope boundary. | Freeze variety/state and label taxonomy before collection. | Y |

### V6 — Software stack

| ID | Claim | Verdict | Evidence | Confidence | Impact | Required correction | Test? |
|---|---|---|---|---|---|---|---|
| SW-01 | Rust on ESP32-S3 with camera/radio | UNVERIFIABLE | `[DS]` esp-rs repositories support ESP-IDF/ESP32-S3 toolchains, but no Rust project, lockfile, C-FFI wrapper or build log is in the repository. RadioLib's C++ integration is therefore unproved. | High | The core firmware path may require a fallback crate or C component. | Build a pinned minimal camera+SX1262 proof; document fallback and toolchain versions. | Y |
| SW-02 | Zig host-only tools | CONFIRMED (scope) | Plan explicitly keeps Zig on the workstation/Pi host for packet/replay/airtime tools and makes no Xtensa claim. No tool exists yet. | High | No MCU portability claim is made. | Add a reproducible host utility when protocol is frozen. | Y |
| SW-03 | Go gateway | UNSUPPORTED | Plan proposes Go service, but no Go source, module file or serial library is present. | High | Gateway cannot be built or audited. | Name/pin a serial library and provide Linux/arm64 build and restart tests. | Y |
| SW-04 | TypeScript dashboard | UNSUPPORTED | Plan proposes React/Vite dashboard, but no TS source or package lock exists. | High | Dashboard support is only a feature statement. | Add package lock, Pi deployment recipe and API contract. | Y |
| SW-05 | LiteRT on Pi | UNVERIFIABLE | `[DS]` LiteRT docs describe Linux embedded/Pi use, but no Pi OS version, Python version, wheel, model or install log exists. | High | Runtime compatibility and inference latency are unknown. | Pin 64-bit OS/Python and exact `ai-edge-litert` wheel; test install and model inference. | Y |
| SW-06 | Mojo workstation-only | CONFIRMED (conservative scope) | `[DS]` Mojo requirements specify supported Linux CPU/RAM baselines; plan keeps Mojo off the Pi/MCU. “Not supported on Pi 5” should remain “not explicitly listed,” not an absolute vendor prohibition. | Medium | Avoids an unsupported deployment dependency. | Record the workstation OS/CPU/RAM used for Mojo experiments. | Y |

### V7 — Memory, flash and storage

| ID | Claim | Verdict | Evidence | Confidence | Impact | Required correction | Test? |
|---|---|---|---|---|---|---|---|
| MS-01 | RAM budgets | CONFIRMED (arithmetic) | `[CE]` 320×240×3=230,400 B (~225 KiB); 640×480×3=921,600 B (~900 KiB); 1600×1200×3=5,760,000 B (~5.49 MiB). | High | Allocation still needs measured heap/DMA headroom. | Log high-water marks with the actual camera driver. | Y |
| MS-02 | Flash layout | INCORRECT as an ESP-IDF table; arithmetic non-overlap confirmed | `[DS]` ESP-IDF partition docs require explicit partition entries; `otadata` is 0x2000 and the default partition table is at 0x8000/0x9000 conventions. Plan line 270 calls its first 64 KiB a concept, but places several unrelated regions there and gives no CSV. App offsets are 64 KiB aligned and do not overlap. | High | OTA cannot be enabled from this concept alone. | Produce a real CSV with bootloader/table/NVS/otadata/PHY, verify sizes/alignment, and check encrypted-flash/key space. | Y |
| MS-03 | Storage calculations | CONFIRMED | `[CE]` 24×100 KiB/day = 2.34375 MiB/day; 30 days = 70.3125 MiB; 10×24×90×8 KiB = 168.75 MiB; originals at 100 KiB = 2.0625 GiB. | High | Filesystem overhead and write endurance remain. | Measure JPEG distribution and reserve free space/retention quotas. | Y |
| MS-04 | Node model slots not Pi model | CONFIRMED | Plan explicitly says 2 MiB optional node slots are for small future models, not the Pi model. | High | Avoids an architecture contradiction. | Keep Pi model storage on gateway. | N |

### V8 — Power

| ID | Claim | Verdict | Evidence | Confidence | Impact | Required correction | Test? |
|---|---|---|---|---|---|---|---|
| PW-01 | Node energy math | CONFIRMED (conditional) | `[CE]` Recomputing the stated currents/durations gives 111.0007 mAh/day, 0.3663 Wh rail/day, 0.4884 Wh/day battery demand, 40.0 days at 0.1 mA sleep, 24.85 days at 3 mA and 12.98 days at 10 mA. Inputs are `[EA]`, not measurements. | High | Arithmetic is correct; autonomy is not established. | Replace assumptions with battery-terminal profiles. | Y |
| PW-02 | 0.1 mA sleep realism | UNVERIFIABLE | Plan calls 0.1 mA a target. No board, regulator, LED, SD-gating or measured sleep trace exists; TPS63070's 50 µA typical Iq is only one component `[DS]`. | High | A development board can reduce autonomy by multiples. | Measure deep sleep at battery terminals through full wake cycle. | Y |
| PW-03 | Solar and dark reserve | CONFIRMED (conditional) | `[CE]` 5 W×3 PSH×0.5=7.5 Wh/day; 7 dark days at 0.4884 Wh/day=3.419 Wh; 6.6 Ah×3.7 V×0.8=19.536 Wh. | High | PSH/derating and battery temperature are assumptions. | Log panel V/I, charge efficiency and reserve through monsoon conditions. | Y |
| PW-04 | Gateway battery/panel | CONFIRMED (arithmetic; load is assumed) | `[CE]` 8 W×24=192 Wh/day; 12.8 V×20 Ah×0.8×0.9=184.32 Wh = 23.04 h; two-day reserve=41.67 Ah; 192/(3×0.65)=98.46 W panel. | High | The 8 W load and Pi supply transients are not measured. | Profile the complete gateway and size LiFePO4 charger/panel from measured load. | Y |
| PW-05 | Brownout/transients | UNSUPPORTED | Plan requests a test but has no schematic, bulk-capacitor value, waveform or pass/fail log. | High | Camera+radio+SD coincidence can reset the node. | Test worst-case simultaneous load with oscilloscope/current probe and brownout logging. | Y |

### V9 — OTA and security

| ID | Claim | Verdict | Evidence | Confidence | Impact | Required correction | Test? |
|---|---|---|---|---|---|---|---|
| SEC-01 | Two OTA slots/metadata | INCORRECT as currently specified | `[DS]` ESP-IDF OTA requires a valid partition table and `otadata`; no CSV exists and the first 64 KiB concept is not valid. | High | OTA boot selection cannot be trusted. | Create and validate the CSV before enabling OTA. | Y |
| SEC-02 | HTTPS OTA/signing/secure boot | UNSUPPORTED | `[DS]` ESP-IDF documents `esp_https_ota`, signed images, secure boot and flash encryption, but repository has no `sdkconfig`, certificates, signing key process or recovery procedure. | High | Release recovery could be lost after eFuse/security activation. | Rehearse unsigned rejection, signed OTA, USB recovery and key custody on sacrificial boards. | Y |
| SEC-03 | Rollback/anti-rollback | UNSUPPORTED | `[DS]` ESP-IDF documents app rollback and anti-rollback; no `CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE`, secure version or `mark_app_valid` code is present. | High | A bad release may brick nodes or silently bypass version policy. | Implement and test interrupted/bad-image rollback and eFuse anti-rollback. | Y |
| SEC-04 | LoRa OTA excluded | CONFIRMED (scope/calculation) | Plan excludes full firmware OTA over raw LoRa; PT-09 independently reproduces the multi-hour airtime. | High | Correctly limits initial scope. | Keep it disabled in the first release. | N |
| SEC-05 | Crypto hygiene | UNSUPPORTED | Plan mentions AEAD/CCM and nonce structure but no HKDF, encrypted NVS/eFuse, rotation/revocation, duplicate-ciphertext handling or test vectors exist. | High | Security claim is design intent only. | Implement a reviewed mbedTLS interface and adversarial replay/nonce tests. | Y |
| SEC-06 | Battery gate for OTA | UNSUPPORTED | Plan says updates need adequate battery/power but defines no threshold, hysteresis or implementation. | High | OTA may brown out during write. | Define threshold from measured energy-to-rollback and implement hysteresis. | Y |

## V.3 Independent calculations

### LoRa time on air

For BW=125,000 Hz, CR=4/5 (`CR=1`), explicit header (`IH=0`), CRC enabled, preamble 8 and LDRO for SF11/12:

```text
T_sym = 2^SF / BW
N_payload = 8 + ceil((8*PL - 4*SF + 28 + 16 - 20*IH)
                     / (4*(SF - 2*DE))) * (CR + 4)
T_packet = (8 + 4.25 + N_payload) * T_sym
```

For PL=240 B:

| SF | T_sym | preamble | N_payload | T_packet |
|---:|---:|---:|---:|---:|
| 7 | 1.024 ms | 12.544 ms | 358 | 0.379136 s |
| 9 | 4.096 ms | 50.176 ms | 278 | 1.188864 s |
| 10 | 8.192 ms | 100.352 ms | 253 | 2.172928 s |
| 11 | 16.384 ms | 200.704 ms | 278 | 4.755456 s |
| 12 | 32.768 ms | 401.408 ms | 248 | 8.527872 s |

Fragments and image airtime with 20% retry allowance (`count × T_packet × 1.2`):

| Image | Fragments | SF7 | SF9 | SF10 | SF11 | SF12 |
|---:|---:|---:|---:|---:|---:|---:|
| 4 KiB | 21 | 9.55 s | 29.96 s | 54.76 s | 119.84 s | 214.90 s |
| 8 KiB | 41 | 18.65 s | 58.49 s | 106.91 s | 233.97 s | 419.57 s |
| 12 KiB | 62 | 28.21 s | 88.45 s | 161.67 s | 353.81 s | 634.47 s |
| 20 KiB | 103 | 46.86 s | 146.94 s | 268.57 s | 587.77 s | 1054.04 s |

The 2.5% daily ceiling is 2,160 s/day. Whole 8 KiB images/day, ignoring telemetry and ACKs, are SF9 36, SF10 20, SF11 9 and SF12 5. A 48-byte ACK is 0.308224 s at SF9 and 2.301952 s at SF12; six ACKs per 8 KiB image are 1.849344 s and 13.811712 s respectively.

### RF path and Fresnel

At 866 MHz, λ=0.34618 m. Using `FSPL=32.44+20log10(d_km)+20log10(866)` gives 91.190 dB at 1 km, 97.211 dB at 2 km, 100.733 dB at 3 km and 105.170 dB at 5 km. Midpoint first-Fresnel radii are 16.113 m and 20.802 m at 3 km and 5 km; 60% clearance is 9.668 m and 12.481 m. The plan's 16.1/20.8 and 9.7/12.5 values reproduce.

With +22 dBm conducted power, 2 dBi node antenna, 5 dBi gateway antenna and zero cable loss, received power is −71.733 dBm at 3 km and −76.170 dBm at 5 km. This is a free-space estimate, not a measured RSSI. Foliage, ground, polarization, connectors, antenna pattern and interference must be de-rated. SX1262 sensitivity values must come from the selected module/data-rate table; SF9 is not established by the product-page summary.

### Storage and power

The plan's storage values reproduce: 24×100 KiB = 2.34375 MiB/day; 30 days = 70.3125 MiB; 10 nodes×24×90×8 KiB = 168.75 MiB; the same originals at 100 KiB = 2.0625 GiB.

The stated hourly current model reproduces 111.0007 mAh/day and 0.4884 Wh/day after 90% conversion and 20% margin. `3.7×6.6×0.8=19.536 Wh`; runtime is 40.0 days at 0.1 mA, 24.85 days at 3 mA and 12.98 days at 10 mA. These are calculated estimates from assumed currents, not measurements. Solar and gateway arithmetic is reproduced in PW-03/PW-04.

## V.4 Implementation findings

The repository inventory found no implementation evidence for the proposed system. `git log -1` identifies an educational-app documentation commit, while the working tree contains Python, Streamlit, Kivy and generated site files. There are no firmware builds, serial/RF logs, camera captures, model packages, dataset manifests, API schema, protocol source, partition CSV or lockfiles. Consequently, no claim that the system “works” can be accepted. The missing evidence directly affects SW-01/03/04/05, PT-07/08, CV-02–05, MS-02, PW-02/05 and SEC-01–06.

The static calculator check was run only in `C:\Users\Lenovo\AppData\Local\Temp\opencode`; no project artifact was modified. Browser execution of the local file was blocked by the browser URL policy, and the parser error is independently decisive.

## V.5 Test requests

The following tests are required to close the unresolved claims. Each needs a recorded setup, measurement, pass/fail result and tool output.

| Area | Setup | Measurement and pass/fail | Tools |
|---|---|---|---|
| Pin/camera bring-up | Exact N16R8 carrier, OV2640 and final GPIO map | 1,000 capture cycles, no DMA/boot conflict, bounded heap; fail on any reserved/strapping conflict | Oscilloscope, ESP-IDF logs, heap high-water marks |
| Image-size study | Same leaf/lighting captured as local VGA and radio derivatives | 4/8/12/20 KiB variants; macro-F1, per-class recall, confidence and rejection; pass only if pre-set field thresholds hold | Frozen model, labelled field set, Python evaluation |
| RF path | Final modules, antennas, 3/5 km surveyed path in mature/wet crop | PER, RSSI, SNR, latency, retries, airtime; pass ≥95% scheduled delivery with legal ledger | Spectrum analyser, packet logger, GPS/path survey |
| Compliance | Final RF BOM and firmware settings | Conducted power, ERP, occupied bandwidth, APC behavior and ETA evidence; fail on any Gazette/ETA mismatch | Calibrated RF power meter/analyser; WPC documentation |
| Protocol/security | Zig/Rust/Go reference vectors and reset injection | Byte-identical reassembly, duplicate ciphertext accepted once, replay rejected, no nonce reuse, retry cap obeyed | Unit tests, property tests, packet fuzzer |
| SD/power loss | SD writes during capture and forced power removal | No committed partial image; journal resumes; pass after 100 interruption cycles | Programmable power switch, filesystem checker |
| Battery/solar | Final board, enclosure, charger, panel and pack | Battery-terminal current over full wake/sleep cycle; brownout-free worst-case capture/TX/SD; charge and 7-day reserve | Current probe, oscilloscope, electronic load, solar logger |
| OTA/security | Sacrificial board with two valid slots | Interrupted HTTPS OTA rolls back; bad signature rejected; anti-rollback enforced; USB recovery retained | ESP-IDF tools, signing keys, serial logs |
| Gateway/runtime | Pi OS 64-bit, pinned Go/Node/Python/model | Reproduce install; measure inference latency, queue recovery and disk retention; pass service restart/atomic commit | Clean Pi image, systemd, benchmark harness |
| Field CV | Agronomist-reviewed plant/plot/date split | Report precision, recall, macro-F1, confidence intervals, false positives/negatives and abstention | Versioned dataset manifest and evaluation notebook |

## V.6 Disagreements with the prior review

The prior review treated the plan as broadly ready because the five-language roles, 8 KiB/SF9 arithmetic, datasets and power numbers were plausible. This verification disagrees in the following material ways:

- Plausible is not implemented: the repository contains no corresponding system code or test evidence.
- The calculator was treated as working, but its JavaScript has a reproducible parse error at the core `toa()` expression.
- 8 KiB hourly is only an engineering schedule under the provisional Table II assumption. Legal status requires product classification and ETA; raw LoRa is not LoRaWAN and an IN865 channel plan does not grant permission.
- The SF9 node airtime calculation is correct, but gateway ACK airtime and other channel users were omitted from the cited total occupancy. SF10+ image frequency violates the 2.5% arithmetic ceiling at the stated hourly rate.
- The first 64 KiB flash concept was not accepted as an ESP-IDF partition table. `otadata` and actual partition entries are required before OTA/security can be verified.
- “Supports Rust, Zig, Go, Mojo and TypeScript” is a deployment plan, not build proof. In particular RadioLib-to-Rust, Go serial, TypeScript deployment, LiteRT wheel selection and Mojo host requirements have no artifacts.
- 3–5 km and 4–8 KiB diagnosticity are conditional hypotheses. Fresnel and FSPL arithmetic reproduces, but vegetation, path clearance, sensitivity and model results remain unmeasured.

## V.7 Open questions for the project owner

1. Which Indian state, tomato variety and first field layout will define the labelled crop and path survey?
2. Which exact ESP32-S3 carrier, OV2640 board, SX1262 module, antenna, charger and regulator will be ordered?
3. Will WPC classify the private raw-LoRa product under Table II, or does Table I/another rule apply? Who will own ETA and RF test responsibility?
4. What is the maximum acceptable image interval and latency when SF11/12 is required?
5. What field metric and minimum per-class sample count will authorize an 8 KiB image policy?
6. Is the gateway mains-powered during the pilot, or must the 8 W load be solar-backed?
7. Which Pi OS/Python/Go/Node versions and model runtime will be supported?
8. What is the key provisioning, secure-boot recovery and OTA rollback owner/process?

## V.8 Residual uncertainty and limits

This report verifies document arithmetic, source facts and artifact presence. It does not certify Indian regulatory compliance, antenna performance, thermal safety, battery life, disease accuracy, or production security. No physical boards, radios, antennas, field path, crop, agronomist labels or final software were available. Vendor maximums are not measured system behavior. FSPL is free-space only; LoRa sensitivity depends on bandwidth, coding, packet configuration and module implementation. Dataset counts/licences are source claims and require attribution/legal review for the intended distribution. The plan should be revised, implemented in a clean repository, and re-verified after the requested tests produce logs and measurements.
