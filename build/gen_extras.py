"""Zed theme, a tmTheme for Sublime Text / bat, and a palette preview script."""
import json, os, plistlib
from palette import load, alpha

def build_zed(dist):
    p = load()
    bg, fg, n, a, t = p["bg"], p["fg"], p["neon"], p["ansi"], p["terminal"]

    def syn(color, style=None, weight=None):
        s = {"color": color}
        if style:
            s["font_style"] = style
        if weight:
            s["font_weight"] = weight
        return s

    style = {
        "background": bg["void"],
        "border": bg["border"],
        "border.variant": bg["raised"],
        "border.focused": n["hex"],
        "border.selected": n["fang"],
        "border.transparent": "#00000000",
        "border.disabled": bg["raised"],
        "elevated_surface.background": bg["panel"],
        "surface.background": bg["crypt"],
        "element.background": bg["panel"],
        "element.hover": bg["raised"],
        "element.active": bg["overlay"],
        "element.selected": bg["raised"],
        "element.disabled": bg["crypt"],
        "drop_target.background": alpha(n["hex"], 30),
        "ghost_element.background": "#00000000",
        "ghost_element.hover": bg["panel"],
        "ghost_element.active": bg["raised"],
        "ghost_element.selected": bg["raised"],
        "ghost_element.disabled": bg["crypt"],
        "text": fg["phosphor"],
        "text.muted": fg["dim"],
        "text.placeholder": fg["muted"],
        "text.disabled": fg["ghost"],
        "text.accent": n["chrome"],
        "icon": fg["dim"],
        "icon.muted": fg["muted"],
        "icon.disabled": fg["ghost"],
        "icon.accent": n["fang"],
        "status_bar.background": bg["crypt"],
        "title_bar.background": bg["void"],
        "toolbar.background": bg["void"],
        "tab_bar.background": bg["crypt"],
        "tab.inactive_background": bg["crypt"],
        "tab.active_background": bg["void"],
        "search.match_background": alpha(n["fang"], 35),
        "panel.background": bg["crypt"],
        "panel.focused_border": n["hex"],
        "pane.focused_border": n["fang"],
        "scrollbar.thumb.background": alpha(n["hex"], 25),
        "scrollbar.thumb.hover_background": alpha(n["hex"], 40),
        "scrollbar.thumb.border": "#00000000",
        "scrollbar.track.background": bg["void"],
        "scrollbar.track.border": bg["crypt"],
        "editor.foreground": fg["phosphor"],
        "editor.background": bg["void"],
        "editor.gutter.background": bg["void"],
        "editor.subheader.background": bg["crypt"],
        "editor.active_line.background": alpha(bg["crypt"], 80),
        "editor.highlighted_line.background": bg["panel"],
        "editor.line_number": fg["ghost"],
        "editor.active_line_number": n["fang"],
        "editor.invisible": bg["raised"],
        "editor.wrap_guide": bg["raised"],
        "editor.active_wrap_guide": bg["overlay"],
        "editor.document_highlight.read_background": alpha(n["chrome"], 18),
        "editor.document_highlight.write_background": alpha(n["fang"], 20),
        "terminal.background": t["background"],
        "terminal.foreground": t["foreground"],
        "terminal.bright_foreground": t["bold"],
        "terminal.dim_foreground": p["crt"]["p1Dim"],
        "terminal.ansi.black": a["black"],
        "terminal.ansi.red": a["red"],
        "terminal.ansi.green": a["green"],
        "terminal.ansi.yellow": a["yellow"],
        "terminal.ansi.blue": a["blue"],
        "terminal.ansi.magenta": a["magenta"],
        "terminal.ansi.cyan": a["cyan"],
        "terminal.ansi.white": a["white"],
        "terminal.ansi.bright_black": a["brightBlack"],
        "terminal.ansi.bright_red": a["brightRed"],
        "terminal.ansi.bright_green": a["brightGreen"],
        "terminal.ansi.bright_yellow": a["brightYellow"],
        "terminal.ansi.bright_blue": a["brightBlue"],
        "terminal.ansi.bright_magenta": a["brightMagenta"],
        "terminal.ansi.bright_cyan": a["brightCyan"],
        "terminal.ansi.bright_white": a["brightWhite"],
        "conflict": n["sodium"],
        "created": n["acid"],
        "deleted": n["wound"],
        "modified": n["chrome"],
        "renamed": n["hex"],
        "hidden": fg["ghost"],
        "ignored": fg["ghost"],
        "predictive": fg["muted"],
        "info": n["chrome"],
        "warning": n["sodium"],
        "error": n["wound"],
        "success": n["acid"],
        "hint": n["hex"],
        "syntax": {
            "attribute": syn(n["sodium"], "italic"),
            "boolean": syn(n["sodium"]),
            "comment": syn(fg["muted"], "italic"),
            "comment.doc": syn(fg["dim"], "italic"),
            "constant": syn(n["sodium"]),
            "constructor": syn(n["hex"]),
            "embedded": syn(fg["phosphor"]),
            "emphasis": syn(n["hexLit"], "italic"),
            "emphasis.strong": syn(n["sodium"], None, 700),
            "enum": syn(n["hex"]),
            "function": syn(n["chrome"], None, 700),
            "function.method": syn(n["chrome"], None, 700),
            "hint": syn(fg["muted"], "italic"),
            "keyword": syn(n["fang"], None, 700),
            "label": syn(n["chromeLit"]),
            "link_text": syn(n["chrome"]),
            "link_uri": syn(n["chromeLit"]),
            "number": syn(n["sodium"]),
            "operator": syn(n["fangLit"]),
            "predictive": syn(fg["muted"], "italic"),
            "preproc": syn(n["sodiumLit"]),
            "primary": syn(fg["phosphor"]),
            "property": syn(n["chromeLit"]),
            "punctuation": syn(fg["dim"]),
            "punctuation.bracket": syn(fg["dim"]),
            "punctuation.delimiter": syn(fg["dim"]),
            "punctuation.list_marker": syn(n["fang"]),
            "punctuation.special": syn(n["fangLit"]),
            "string": syn(n["acid"]),
            "string.escape": syn(n["chromeLit"]),
            "string.regex": syn(n["chromeLit"]),
            "string.special": syn(n["acidLit"]),
            "string.special.symbol": syn(n["acidLit"]),
            "tag": syn(n["fang"], None, 700),
            "text.literal": syn(n["acid"]),
            "title": syn(n["fang"], None, 800),
            "type": syn(n["hex"]),
            "variable": syn(fg["phosphor"]),
            "variable.special": syn(n["hex"], "italic"),
            "variant": syn(n["hex"]),
        },
        "players": [
            {"cursor": n["fang"], "background": n["fang"], "selection": alpha(n["hex"], 30)},
            {"cursor": n["chrome"], "background": n["chrome"], "selection": alpha(n["chrome"], 25)},
            {"cursor": n["acid"], "background": n["acid"], "selection": alpha(n["acid"], 25)},
            {"cursor": n["sodium"], "background": n["sodium"], "selection": alpha(n["sodium"], 25)},
        ],
    }

    doc = {
        "$schema": "https://zed.dev/schema/themes/v0.2.0.json",
        "name": p["name"],
        "author": p["author"],
        "themes": [{"name": p["name"], "appearance": "dark", "style": style}],
    }
    d = os.path.join(dist, "zed")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f'{p["slug"]}.json')
    with open(path, "w") as f:
        json.dump(doc, f, indent=2)
        f.write("\n")
    return path


def build_tmtheme(dist):
    """Covers Sublime Text and `bat`, which both eat tmTheme."""
    p = load()
    bg, fg, n = p["bg"], p["fg"], p["neon"]

    def rule(name, scope, fgc=None, style=None, bgc=None):
        s = {}
        if fgc: s["foreground"] = fgc
        if bgc: s["background"] = bgc
        if style: s["fontStyle"] = style
        return {"name": name, "scope": scope, "settings": s}

    settings = [
        {"settings": {
            "background": bg["void"],
            "foreground": fg["phosphor"],
            "caret": n["fang"],
            "lineHighlight": bg["crypt"],
            "selection": bg["overlay"],
            "selectionBorder": n["hex"],
            "invisibles": bg["raised"],
            "gutterForeground": fg["ghost"],
            "guide": bg["raised"],
            "activeGuide": n["hex"],
            "stackGuide": bg["overlay"],
            "findHighlight": n["fang"],
            "findHighlightForeground": bg["void"],
        }},
        rule("Comment", "comment", fg["muted"], "italic"),
        rule("String", "string", n["acid"]),
        rule("Escape", "constant.character.escape, string.regexp", n["chromeLit"]),
        rule("Number/Constant", "constant.numeric, constant.language, constant.other, support.constant", n["sodium"]),
        rule("Keyword", "keyword, storage, storage.type, storage.modifier", n["fang"], "bold"),
        rule("Operator", "keyword.operator", n["fangLit"]),
        rule("Function", "entity.name.function, support.function, meta.function-call", n["chrome"], "bold"),
        rule("Type/Class", "entity.name.type, entity.name.class, support.type, support.class, entity.other.inherited-class", n["hex"]),
        rule("Variable", "variable, variable.other", fg["phosphor"]),
        rule("Parameter", "variable.parameter", fg["dim"], "italic"),
        rule("Property", "variable.other.property, support.type.property-name, meta.object-literal.key", n["chromeLit"]),
        rule("Language variable", "variable.language", n["hex"], "italic"),
        rule("Tag", "entity.name.tag", n["fang"], "bold"),
        rule("Attribute", "entity.other.attribute-name", n["sodium"], "italic"),
        rule("Punctuation", "punctuation, meta.brace", fg["dim"]),
        rule("Invalid", "invalid", n["wound"], "bold"),
        rule("Heading", "markup.heading", n["fang"], "bold"),
        rule("Bold", "markup.bold", n["sodium"], "bold"),
        rule("Italic", "markup.italic", n["hexLit"], "italic"),
        rule("Link", "markup.underline.link", n["chrome"], "underline"),
        rule("Raw", "markup.raw, markup.inline.raw", n["acid"]),
        rule("Inserted", "markup.inserted", n["acid"]),
        rule("Deleted", "markup.deleted", n["wound"]),
        rule("Changed", "markup.changed", n["chrome"]),
        rule("Diff header", "meta.diff.header, meta.diff.range", n["hex"], "bold"),
    ]

    doc = {
        "name": p["name"],
        "semanticClass": "theme.dark.neonferatu",
        "uuid": f'7f3c1c2e-9b1a-4f2a-9c31-{p["slug"][:12]:*<12}',
        "colorSpaceName": "sRGB",
        "settings": settings,
    }
    d = os.path.join(dist, "tmtheme")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f'{p["slug"]}.tmTheme')
    with open(path, "wb") as f:
        plistlib.dump(doc, f, fmt=plistlib.FMT_XML)
    return path
