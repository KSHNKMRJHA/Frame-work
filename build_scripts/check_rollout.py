"""Guard supported SignalBench presentation across the whole application."""
import ast
import copy
import re
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
PRIMITIVES = {
    "page_hero", "protocol_hero", "section_header", "info_badge",
    "engineering_metric", "callout", "spec_table", "status_led",
}


def component_calls(tree):
    return {
        node.func.attr for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name) and node.func.value.id == "components"
    }


def quiz_progress():
    """The live native quiz updates progress and persists a submission once.

    Stub persistence so this check never reads or writes a learner's profile.
    """
    from streamlit.testing.v1 import AppTest
    from utils import state

    quiz_page = next((ROOT / "pages").glob("8_*.py"))
    with patch.object(state, "load_state", return_value=copy.deepcopy(state.DEFAULT_STATE)), patch.object(state, "save_state") as saved:
        app = AppTest.from_file(str(quiz_page)).run()
        next(b for b in app.button if "Start New Quiz" in b.label).click().run()
        assert len(app.radio) == 10 and not app.exception
        for i in range(3):
            app.radio[i].set_value(app.radio[i].options[0]).run()
        assert app.get("progress")[0].proto.value == 30
        next(b for b in app.button if "Submit Quiz" in b.label).click().run()
        assert not app.exception and app.session_state["quiz_submitted"]
        assert all(r.disabled for r in app.radio)
        assert saved.call_count == 1


def check():
    pages = [ROOT / "app.py", *sorted((ROOT / "pages").glob("*.py"))]
    for path in pages:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        calls = component_calls(tree)
        assert calls & PRIMITIVES, f"{path.name}: missing approved components"
        if path.name == "app.py":
            assert "engineering_metric" in calls, path.name
        elif path.name.startswith("1_"):
            assert "protocol_hero" in calls and "spec_table" in calls, path.name
        else:
            assert "page_hero" in calls, path.name
    for path in [*pages, *sorted((ROOT / "utils").glob("*.py"))]:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        docstrings = {
            id(node.value) for node in ast.walk(tree)
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings:
                assert not re.search(r"<\s*(style|script)\b", node.value, re.I), path.name
                assert not re.search(r"class\s*=.*\bfw-", node.value), path.name
            if isinstance(node, ast.Attribute):
                name = ast.unparse(node)
                assert not name.startswith(("st._", "st.context._")), (path.name, name)
            if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                assert all(ast.unparse(t) != "st.context.theme" for t in targets), path.name
            if isinstance(node, ast.Call):
                name = ast.unparse(node.func)
                assert name not in {"st.set_option", "st.config.set_option", "theme.set_theme"}, (path.name, name)
    settings = next((ROOT / "pages").glob("11_*.py")).read_text(encoding="utf-8")
    assert "active_theme_type()" in settings and "Streamlit's own menu" in settings
    assert not re.search(r"(?:write_text|open).*config\.toml", settings)
    quiz_progress()
    print(f"Rollout checks passed: {len(pages)} pages; supported markup, native theme ownership")


if __name__ == "__main__":
    check()
