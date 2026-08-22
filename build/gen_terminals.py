"""iTerm2 .itermcolors and Terminal.app .terminal profiles."""
import base64, os, plistlib
from palette import load, hex_to_floats

ITERM_KEYS = [
    ("Ansi 0 Color",  ("ansi", "black")),
    ("Ansi 1 Color",  ("ansi", "red")),
    ("Ansi 2 Color",  ("ansi", "green")),
    ("Ansi 3 Color",  ("ansi", "yellow")),
    ("Ansi 4 Color",  ("ansi", "blue")),
    ("Ansi 5 Color",  ("ansi", "magenta")),
    ("Ansi 6 Color",  ("ansi", "cyan")),
    ("Ansi 7 Color",  ("ansi", "white")),
    ("Ansi 8 Color",  ("ansi", "brightBlack")),
    ("Ansi 9 Color",  ("ansi", "brightRed")),
    ("Ansi 10 Color", ("ansi", "brightGreen")),
    ("Ansi 11 Color", ("ansi", "brightYellow")),
    ("Ansi 12 Color", ("ansi", "brightBlue")),
    ("Ansi 13 Color", ("ansi", "brightMagenta")),
    ("Ansi 14 Color", ("ansi", "brightCyan")),
    ("Ansi 15 Color", ("ansi", "brightWhite")),
    ("Background Color",     ("terminal", "background")),
    ("Foreground Color",     ("terminal", "foreground")),
    ("Bold Color",           ("terminal", "bold")),
    ("Cursor Color",         ("terminal", "cursor")),
    ("Cursor Text Color",    ("terminal", "cursorText")),
    ("Selection Color",      ("terminal", "selection")),
    ("Selected Text Color",  ("terminal", "selectionText")),
    ("Link Color",           ("terminal", "link")),
    ("Badge Color",          ("terminal", "badge")),
    ("Tab Color",            ("terminal", "tabActive")),
    ("Cursor Guide Color",   ("bg", "raised")),
]


def _iterm_color(hexstr):
    r, g, b = hex_to_floats(hexstr)
    return {
        "Color Space": "sRGB",
        "Red Component": r,
        "Green Component": g,
        "Blue Component": b,
        "Alpha Component": 1.0,
    }


def build_iterm(dist):
    p = load()
    out = {k: _iterm_color(p[grp][key]) for k, (grp, key) in ITERM_KEYS}
    d = os.path.join(dist, "iterm2")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f'{p["slug"]}.itermcolors')
    with open(path, "wb") as f:
        plistlib.dump(out, f, fmt=plistlib.FMT_XML)
    return path


# --- Terminal.app needs NSKeyedArchiver blobs, not plain values -------------

def _archived_color(hexstr):
    r, g, b = hex_to_floats(hexstr)
    rgb = f"{r:.6f} {g:.6f} {b:.6f}".encode() + b"\x00"
    plist = {
        "$version": 100000,
        "$archiver": "NSKeyedArchiver",
        "$top": {"root": plistlib.UID(1)},
        "$objects": [
            "$null",
            {"$class": plistlib.UID(2), "NSColorSpace": 1, "NSRGB": rgb},
            {"$classes": ["NSColor", "NSObject"], "$classname": "NSColor"},
        ],
    }
    return plistlib.dumps(plist, fmt=plistlib.FMT_BINARY)


def _archived_font(name, size):
    plist = {
        "$version": 100000,
        "$archiver": "NSKeyedArchiver",
        "$top": {"root": plistlib.UID(1)},
        "$objects": [
            "$null",
            {"$class": plistlib.UID(3), "NSName": plistlib.UID(2),
             "NSSize": float(size), "NSfFlags": 16},
            name,
            {"$classes": ["NSFont", "NSObject"], "$classname": "NSFont"},
        ],
    }
    return plistlib.dumps(plist, fmt=plistlib.FMT_BINARY)


TERM_KEYS = [
    ("ANSIBlackColor",         ("ansi", "black")),
    ("ANSIRedColor",           ("ansi", "red")),
    ("ANSIGreenColor",         ("ansi", "green")),
    ("ANSIYellowColor",        ("ansi", "yellow")),
    ("ANSIBlueColor",          ("ansi", "blue")),
    ("ANSIMagentaColor",       ("ansi", "magenta")),
    ("ANSICyanColor",          ("ansi", "cyan")),
    ("ANSIWhiteColor",         ("ansi", "white")),
    ("ANSIBrightBlackColor",   ("ansi", "brightBlack")),
    ("ANSIBrightRedColor",     ("ansi", "brightRed")),
    ("ANSIBrightGreenColor",   ("ansi", "brightGreen")),
    ("ANSIBrightYellowColor",  ("ansi", "brightYellow")),
    ("ANSIBrightBlueColor",    ("ansi", "brightBlue")),
    ("ANSIBrightMagentaColor", ("ansi", "brightMagenta")),
    ("ANSIBrightCyanColor",    ("ansi", "brightCyan")),
    ("ANSIBrightWhiteColor",   ("ansi", "brightWhite")),
    ("BackgroundColor",        ("terminal", "background")),
    ("TextColor",              ("terminal", "foreground")),
    ("TextBoldColor",          ("terminal", "bold")),
    ("CursorColor",            ("terminal", "cursor")),
    ("SelectionColor",         ("terminal", "selection")),
]


def build_terminal_app(dist, font_postscript):
    p = load()
    prof = {k: _archived_color(p[grp][key]) for k, (grp, key) in TERM_KEYS}
    prof.update({
        "name": p["name"],
        "type": "Window Settings",
        "ProfileCurrentVersion": 2.07,
        "Font": _archived_font(font_postscript, p["font"]["termSize"]),
        "FontAntialias": True,
        "FontWidthSpacing": 1.0,
        "FontHeightSpacing": p["font"]["lineHeight"],
        "CursorType": 0,
        "CursorBlink": True,
        "BlinkText": False,
        "ShowWindowSettingsNameInTitle": False,
        "columnCount": 120,
        "rowCount": 34,
        "ShouldLimitScrollback": 0,
        "UseBrightBold": True,
        "useOptionAsMetaKey": True,
    })
    d = os.path.join(dist, "terminal-app")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f'{p["slug"]}.terminal')
    with open(path, "wb") as f:
        plistlib.dump(prof, f, fmt=plistlib.FMT_XML)
    return path


# --- iTerm2 dynamic profile: drops into place live, no restart, no plist surgery
DYNAMIC_GUID = "neonferatu-0001-cyberpunk"

def build_iterm_dynamic(dist):
    p = load()
    prof = {k: _iterm_color(p[grp][key]) for k, (grp, key) in ITERM_KEYS}
    f = p["font"]
    prof.update({
        "Name": p["name"],
        "Guid": f'{p["slug"]}-dynamic-profile',
        "Dynamic Profile Parent Name": "Default",
        "Normal Font": f'{f["postscript"]} {f["termSize"]}',
        "Non Ascii Font": f'{f["postscript"]} {f["termSize"]}',
        "Use Non-ASCII Font": False,
        "Horizontal Spacing": 1.0,
        "Vertical Spacing": round(f["lineHeight"] - 0.35, 2),
        "Use Bold Font": True,
        "Use Bright Bold": True,
        "Use Italic Font": True,
        "Cursor Type": 2,
        "Blinking Cursor": True,
        "Blur": True,
        "Blur Radius": 8.0,
        "Transparency": 0.06,
        "Columns": 120,
        "Rows": 34,
        "Unlimited Scrollback": True,
        "Custom Directory": "Recycle",
        "Minimum Contrast": 0.0,
        "Badge Color": _iterm_color(p["terminal"]["badge"]),
    })
    d = os.path.join(dist, "iterm2")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f'{p["slug"]}.dynamic-profile.json')
    with open(path, "w") as fh:
        import json as _json
        _json.dump({"Profiles": [prof]}, fh, indent=2)
        fh.write("\n")
    return path


# --- OSC 1337 SetColors: repaint the session you are sitting in, right now
OSC_MAP = [
    ("bg", ("terminal", "background")), ("fg", ("terminal", "foreground")),
    ("bold", ("terminal", "bold")), ("link", ("terminal", "link")),
    ("selbg", ("terminal", "selection")), ("selfg", ("terminal", "selectionText")),
    ("curbg", ("terminal", "cursor")), ("curfg", ("terminal", "cursorText")),
    ("black", ("ansi", "black")), ("red", ("ansi", "red")),
    ("green", ("ansi", "green")), ("yellow", ("ansi", "yellow")),
    ("blue", ("ansi", "blue")), ("magenta", ("ansi", "magenta")),
    ("cyan", ("ansi", "cyan")), ("white", ("ansi", "white")),
    ("br_black", ("ansi", "brightBlack")), ("br_red", ("ansi", "brightRed")),
    ("br_green", ("ansi", "brightGreen")), ("br_yellow", ("ansi", "brightYellow")),
    ("br_blue", ("ansi", "brightBlue")), ("br_magenta", ("ansi", "brightMagenta")),
    ("br_cyan", ("ansi", "brightCyan")), ("br_white", ("ansi", "brightWhite")),
]

def build_live_script(dist):
    p = load()
    pairs = [f'  {k}={p[grp][key].lstrip("#").lower()}' for k, (grp, key) in OSC_MAP]
    body = "\n".join([
        "#!/usr/bin/env bash",
        "# Repaint the CURRENT iTerm2 session in Neonferatu. Lasts until the tab closes;",
        "# for permanence use the Neonferatu profile that install.py drops in.",
        "colors=(",
        *pairs,
        ")",
        'for c in "${colors[@]}"; do',
        '  printf "\\033]1337;SetColors=%s\\a" "$c"',
        "done",
        'printf "\\033[0m"',
        "",
    ])
    path = os.path.join(dist, "iterm2", "live.sh")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(body)
    os.chmod(path, 0o755)
    return path
