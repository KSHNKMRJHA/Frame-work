#!/usr/bin/env python3
"""Generate API reference stubs for mkdocstrings.

This script creates .md files in docs/api/ that mkdocstrings will populate
with auto-generated documentation from docstrings.
"""

from pathlib import Path

API_DIR = Path(__file__).parent / "api"
API_DIR.mkdir(exist_ok=True)

MODULES = {
    "data_loader": "utils.data_loader",
    "diagrams": "utils.diagrams",
    "mindmap": "utils.mindmap",
    "quiz_engine": "utils.quiz_engine",
    "science": "utils.science",
    "state": "utils.state",
    "branding": "utils.branding",
}

TEMPLATE = """# API: {title}

::: {module}
    options:
      show_source: true
      show_root_heading: true
      show_category_heading: true
      members_order: source
      filters: ["!^_"]
      docstring_style: google
"""

def main():
    for name, module in MODULES.items():
        title = name.replace("_", " ").title()
        content = TEMPLATE.format(title=title, module=module)
        (API_DIR / f"{name}.md").write_text(content, encoding="utf-8")
        print(f"Generated: docs/api/{name}.md")

if __name__ == "__main__":
    main()
