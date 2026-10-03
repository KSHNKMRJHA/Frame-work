"""Guard the Streamlit compatibility floor.

requirements.txt declares `streamlit>=X`. That bound is only honest if the
features we actually use arrived no later than X, and this script makes the
claim checkable instead of aspirational:

1. The installed Streamlit satisfies the declared floor.
2. Every key in `.streamlit/config.toml` under `[theme]` (and its
   `[theme.sidebar]`, `[theme.light]`, ... subsections) is a key the *installed*
   Streamlit recognises.

Check 2 is the important one. Streamlit silently ignores theme keys it does not
understand, so a typo or a key that is newer than the floor produces a quietly
wrong-looking app rather than an error. Asking Streamlit itself for the valid
key set turns that into a hard failure.

Feature history that sets the floor (see requirements.txt for the summary):

    1.40.0  st.pills, st.segmented_control
    1.47.0  theme.linkUnderline, theme.dataframeHeaderBackgroundColor
    1.48.0  width= on button / link_button / form_submit_button
    1.49.0  width= on pyplot / image / dataframe, st.dialog(width=)
    1.51.0  theme.sidebar and theme.light sections, st.plotly_chart(width=)
    1.55.0  theme.metricValueFontWeight

Exit codes: 0 = all good, 1 = a real incompatibility.
"""

from __future__ import annotations

import pathlib
import re
import sys
import tomllib

try:
    import streamlit
    import streamlit.config as st_config
except ImportError as exc:  # pragma: no cover
    sys.exit(f"streamlit is not importable: {exc}")

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / ".streamlit" / "config.toml"
REQUIREMENTS = ROOT / "requirements.txt"


def declared_floor() -> tuple[int, ...]:
    """Read `streamlit>=X.Y.Z` out of requirements.txt."""
    for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*streamlit\s*>=\s*([0-9]+(?:\.[0-9]+)*)", line)
        if m:
            return tuple(int(p) for p in m.group(1).split("."))
    sys.exit(f"no `streamlit>=` requirement found in {REQUIREMENTS}")


def parse_version(text: str) -> tuple[int, ...]:
    """Best-effort numeric version, ignoring any rc/local suffix."""
    return tuple(int(p) for p in re.match(r"(\d+(?:\.\d+)*)", text).group(1).split("."))


def valid_theme_options() -> set[str]:
    """Full dotted theme option names the installed Streamlit recognises.

    Names look like `theme.primaryColor`, `theme.sidebar.primaryColor`,
    `theme.light.backgroundColor` or `theme.dark.sidebar.borderColor`.
    """
    getter = getattr(st_config, "get_config_options", None)
    if getter is None:  # pragma: no cover - private API drift
        sys.exit("streamlit.config.get_config_options() is missing; "
                 "the private API changed - update this check")
    return {name for name in getter() if name.startswith("theme.")}


# The section prefixes Streamlit accepts under [theme].
SECTIONS = ("theme", "theme.sidebar", "theme.light", "theme.dark",
            "theme.light.sidebar", "theme.dark.sidebar")


def configured_theme_keys(data: dict) -> list[tuple[str, str]]:
    """Return (section, key) pairs for every key configured under [theme].

    Handles both plain keys and the section tables Streamlit supports:
    `[theme.sidebar]`, `[theme.light]`, `[theme.light.sidebar]`, ...
    """
    theme = data.get("theme", {})
    found: list[tuple[str, str]] = []
    for key, value in theme.items():
        if isinstance(value, dict):
            # A table. Its own name is a section, and its children are keys in
            # that section - `[theme.light]` holds keys, `[theme.light.sidebar]`
            # is itself a section of `[theme.light]`.
            section = f"theme.{key}"
            for subkey, subvalue in value.items():
                if isinstance(subvalue, dict):
                    for deepkey in subvalue:
                        found.append((f"{section}.{subkey}", deepkey))
                else:
                    found.append((section, subkey))
        else:
            found.append(("theme", key))
    return found


def main() -> int:
    failures: list[str] = []

    floor = declared_floor()
    installed = parse_version(streamlit.__version__)
    print(f"declared floor : streamlit>={'.'.join(map(str, floor))}")
    print(f"installed      : streamlit {streamlit.__version__}")
    if installed < floor:
        failures.append(
            f"installed Streamlit {streamlit.__version__} is older than the "
            f"declared floor {'.'.join(map(str, floor))}"
        )

    if not CONFIG.exists():
        failures.append(f"missing {CONFIG}")
        data: dict = {}
    else:
        with CONFIG.open("rb") as fh:
            data = tomllib.load(fh)

    if data:
        used = configured_theme_keys(data)

        # Validate `base` BEFORE asking Streamlit anything: an invalid value
        # makes Streamlit's own theme loader treat it as a theme file path and
        # raise a confusing FileNotFoundError.
        base = data.get("theme", {}).get("base")
        if base not in (None, "light", "dark"):
            failures.append(
                f"[theme] base must be 'light' or 'dark', got {base!r} "
                "(anything else is interpreted by Streamlit as a theme file path)"
            )

        try:
            known = valid_theme_options()
        except Exception as exc:
            print("\nSTREAMLIT FLOOR CHECK FAILED", file=sys.stderr)
            for f in failures:
                print(f"  - {f}", file=sys.stderr)
            print(f"  - could not read the theme option registry: {exc}", file=sys.stderr)
            return 1

        print(f"theme keys     : {len(used)} used, {len(known)} recognised by this build")
        for section, key in sorted(used):
            if not any(f"{section}.{key}" in known for section in SECTIONS):
                failures.append(
                    f"[{section}] theme key {key!r} is not recognised by "
                    f"Streamlit {streamlit.__version__} - it will be silently ignored"
                )

    if failures:
        print("\nSTREAMLIT FLOOR CHECK FAILED", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("\nStreamlit floor OK: declared bound is satisfied and every theme key "
          "is recognised.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
