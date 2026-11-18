import plistlib
import re
import sys
from pathlib import Path

import pytest

from deepwick_spec.check_port import check_port
from deepwick_spec.palette import load_palette

REPO = Path(__file__).resolve().parents[1]
PALETTE = load_palette()
C = {name: value.upper() for name, value in PALETTE.colors.items()}
sys.path.insert(0, str(REPO))
FILE = REPO / "deepwick.tmTheme"
HEX = re.compile(r"#[0-9A-F]{6}")


def load():
    with open(FILE, "rb") as f:
        return plistlib.load(f)


def resolve(scope):
    """Style for a one-scope stack, as syntect's style_mod_for_stack sees it.

    A selector atom matches when it is a dot-wise prefix of the scope; the
    longest match wins and later rules win ties. Descendant selectors need a
    deeper stack, so they never match here.
    """
    parts = scope.split(".")
    best = {}
    for rule in load()["settings"][1:]:
        score = 0
        for atom in (a.strip() for a in rule["scope"].split(",")):
            if " " in atom:
                continue
            a = atom.split(".")
            if parts[: len(a)] == a:
                score = max(score, len(a))
        if score:
            for key, value in rule["settings"].items():
                if key not in best or score >= best[key][0]:
                    best[key] = (score, value)
    return {key: value for key, (_, value) in best.items()}


def test_valid_plist_named_deepwick():
    theme = load()
    assert theme["name"] == "Deepwick"
    globals_ = theme["settings"][0]["settings"]
    assert globals_["background"] == C["background"]
    assert globals_["foreground"] == C["foreground"]
    assert globals_["selection"] == C["selection"]


def test_every_color_is_uppercase_hex():
    for rule in load()["settings"]:
        for key in ("foreground", "background"):
            if key in rule["settings"]:
                assert HEX.fullmatch(rule["settings"][key]), rule


def test_committed_file_matches_generator():
    import generate

    assert FILE.read_bytes() == generate.theme(PALETTE)


# Scopes the Codex TUI (0.170.0) queries outside code highlighting.
CHROME = {
    "codex.accent": "blue",
    "markup.heading.1.markdown": "blue",
    "markup.heading.markdown": "blue",
    "markup.inline.raw.string.markdown": "orange",
    "markup.raw.inline.markdown": "orange",
    "markup.list.numbered.markdown": "blue",
    "markup.list.unnumbered.markdown": "blue",
    "markup.list.bullet.markdown": "blue",
    "markup.underline.link.markdown": "orange",
    "markup.quote.markdown": "comment",
    "entity.name.type": "teal",
    "string": "orange",
    "entity.name.function": "yellow",
    "keyword.control": "magenta",
    "constant.numeric": "sage",
    "constant.language": "blue",
    "comment": "comment",
    "storage.modifier": "blue",
    "markup.heading": "blue",
    "entity.name.section": "blue",
    "markup.inserted": "green",
    "markup.deleted": "red",
}


@pytest.mark.parametrize("scope,role", CHROME.items())
def test_chrome_scope_foreground(scope, role):
    assert resolve(scope).get("foreground") == C[role]


@pytest.mark.parametrize("scope", ["markup.bold.markdown", "markup.italic.markdown"])
def test_emphasis_keeps_text_color(scope):
    style = resolve(scope)
    assert "foreground" not in style
    assert style["fontStyle"] in ("bold", "italic")


@pytest.mark.parametrize(
    "scope,role",
    [("markup.inserted", "diffAdded"), ("diff.inserted", "diffAdded"),
     ("markup.deleted", "diffRemoved"), ("diff.deleted", "diffRemoved")],
)
def test_diff_backgrounds(scope, role):
    assert resolve(scope)["background"] == C[role]


def test_headings_are_bold():
    assert resolve("markup.heading.2.markdown")["fontStyle"] == "bold"


def test_readme_installs_the_file_under_its_config_name():
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    assert 'theme = "deepwick"' in readme
    assert "themes/deepwick.tmTheme" in readme


def test_port_conventions():
    assert check_port(REPO, PALETTE.allowed_hex()) == []
