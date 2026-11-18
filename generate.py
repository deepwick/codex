"""Write deepwick.tmTheme, the Codex CLI syntax theme, from the Deepwick palette.

The rules follow Deepwick for bat, plus the scopes the Codex TUI reads for its
own chrome (accent, diff backgrounds, Markdown, status line).

Run from this directory: PYTHONPATH=../spec python3 generate.py
"""
import plistlib
from pathlib import Path

from deepwick_spec.palette import Palette, load_palette

OUT = Path(__file__).with_name("deepwick.tmTheme")

GLOBALS = {
    "background": "background",
    "foreground": "foreground",
    "caret": "foreground",
    "lineHighlight": "surface",
    "selection": "selection",
    "findHighlight": "selection",
    "gutter": "background",
    "gutterForeground": "muted",
    "invisibles": "overlay",
    "guide": "overlay",
}

# (scope selector, foreground role, background role, fontStyle)
RULES = (
    ("codex.accent", "blue", None, None),
    ("comment, punctuation.definition.comment, string.quoted.docstring, keyword.other.documentation, storage.type.class.jsdoc, storage.type.class.doxygen", "comment", None, "italic"),
    ("keyword, storage.type, storage.modifier, constant.language, constant.other, variable.language, keyword.other.using, keyword.other.namespace", "blue", None, None),
    ("keyword.control, keyword.operator.new, keyword.operator.expression, keyword.operator.cast, keyword.operator.sizeof, keyword.control.import, keyword.control.export, keyword.control.from", "magenta", None, None),
    ("keyword.operator, punctuation", "foreground", None, None),
    ("entity.name.type, entity.name.class, entity.name.namespace, entity.name.scope-resolution, support.class, support.type", "teal", None, None),
    ("entity.name.type.interface, entity.name.interface, entity.name.type.enum, entity.name.enum, entity.name.type.enum-member, entity.name.type.struct, entity.name.struct, storage.type.struct", "mint", None, None),
    ("entity.name.function, entity.name.function.member, support.function, meta.function-call, support.function.magic, entity.name.function.decorator, variable.annotation, punctuation.definition.annotation", "yellow", None, None),
    ("entity.name.function.macro, entity.name.macro, entity.name.constant.preprocessor, entity.name.function.preprocessor", "magenta", None, None),
    ("variable, entity.name.variable, variable.parameter, variable.other.property, variable.other.object.property, entity.other.attribute-name, support.type.property-name", "lightBlue", None, None),
    ("variable.language", "blue", None, None),
    ("variable.other.constant", "cyan", None, None),
    ("string, punctuation.definition.string, string.quoted.include, string.quoted.other.lt-gt.include, punctuation.definition.string.begin.include, punctuation.definition.string.end.include, support.constant.property-value", "orange", None, None),
    ("string.quoted.docstring, comment.block.documentation", "comment", None, "italic"),
    ("constant.character.escape, entity.other.attribute-name.class.css, entity.other.attribute-name.id.css, punctuation.definition.group.regexp, punctuation.definition.character-class.regexp", "gold", None, None),
    ("string.regexp", "rose", None, None),
    ("constant.numeric", "sage", None, None),
    ("entity.name.tag", "blue", None, None),
    ("punctuation.definition.tag", "muted", None, None),
    ("meta.preprocessor", "muted", None, "bold"),
    ("keyword.control.directive, keyword.preprocessor, meta.preprocessor keyword.control.import", "foreground", None, None),
    ("entity.name.label", "foreground", None, None),
    ("markup.heading, entity.name.section", "blue", None, "bold"),
    ("markup.bold", None, None, "bold"),
    ("markup.italic", None, None, "italic"),
    ("markup.underline.link, markup.inline.raw, markup.fenced_code.block, markup.raw", "orange", None, None),
    ("markup.quote", "comment", None, None),
    ("markup.list, punctuation.definition.list_item, punctuation.definition.list.begin", "blue", None, None),
    ("markup.inserted, diff.inserted, meta.diff.header.to-file", "green", "diffAdded", None),
    ("markup.deleted, diff.deleted, meta.diff.header.from-file", "red", "diffRemoved", None),
    ("markup.changed, meta.diff.range, meta.diff.index", "blue", None, None),
    ("invalid", "red", None, None),
    ("invalid.deprecated", "foreground", None, "strikethrough"),
)


def theme(palette: Palette) -> bytes:
    c = {name: value.upper() for name, value in palette.colors.items()}
    settings: list[dict] = [{"settings": {key: c[role] for key, role in GLOBALS.items()}}]
    for scope, fg, bg, font in RULES:
        style = {}
        if fg:
            style["foreground"] = c[fg]
        if bg:
            style["background"] = c[bg]
        if font:
            style["fontStyle"] = font
        settings.append({"scope": scope, "settings": style})
    doc = {"name": "Deepwick", "semanticClass": "theme.dark.deepwick", "settings": settings}
    return plistlib.dumps(doc, sort_keys=False)


if __name__ == "__main__":
    OUT.write_bytes(theme(load_palette()))
    print(f"wrote {OUT.name}")
