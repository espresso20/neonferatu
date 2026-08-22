#!/usr/bin/env python3
"""Regenerate the generated blocks inside README.md.

The palette table in the README was hand-maintained and went stale the moment
an accent moved — the same failure mode as ansi.* copying neon.*. It is now
written from palette.json between markers.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import color
from palette import ROOT, load, variants

ROLES = [
    ("bg.void",      "editor background"),
    ("bg.crypt",     "sidebars, panels, status bar"),
    ("bg.panel",     "popovers, inputs, menus"),
    ("bg.raised",    "selected rows, ANSI black"),
    ("bg.border",    "every 1px line in the UI"),
    ("bg.overlay",   "selection fill"),
    ("fg.phosphor",  "body text"),
    ("fg.dim",       "secondary text, parameters"),
    ("fg.muted",     "comments"),
    ("fg.ghost",     "line numbers, disabled"),
    ("neon.fang",    "**keywords**, cursor, Claude"),
    ("neon.chrome",  "functions, links, properties"),
    ("neon.hex",     "types and classes"),
    ("neon.acid",    "strings, success, additions"),
    ("neon.sodium",  "numbers, constants, warnings"),
    ("neon.wound",   "errors, deletions"),
    ("neon.coolant", "ANSI blue, IDE chrome"),
    ("crt.glass",    "**terminal background** — unlit tube"),
    ("crt.p1",       "P1 phosphor, the classic green"),
    ("crt.p3Amber",  "P3 amber, the other classic"),
]


def get(pal, path):
    node = pal
    for part in path.split("."):
        node = node[part]
    return node


def table():
    pal = load()
    bg = pal["bg"]["void"]
    out = ["| role | hex | L\\* | chroma | contrast | where it lands |",
           "|---|---|---:|---:|---:|---|"]
    for path, where in ROLES:
        v = get(pal, path)
        L, C, _ = color.to_oklch(v)
        ratio = color.contrast(v, bg)
        r = "—" if path.startswith("bg.") else f"{ratio:.2f}:1"
        out.append(f"| `{path}` | `{v}` | {L:.1f} | {C:.3f} | {r} | {where} |")
    return "\n".join(out)


def variant_table():
    out = ["| variant | anchor | what it is |", "|---|---|---|"]
    for vname, pal in variants():
        anchor = pal.get("anchorHue")
        a = f"H{anchor:.0f}" if anchor is not None else "—"
        label = "*(base)*" if not vname else f"`{vname}`"
        out.append(f"| {label} | {a} | {pal['blurb']} |")
    return "\n".join(out)


BLOCKS = {"palette": table, "variants": variant_table}


def build(_dist=None):
    path = os.path.join(ROOT, "README.md")
    src = open(path).read()
    for name, fn in BLOCKS.items():
        start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
        if start not in src or end not in src:
            continue
        head = src[:src.index(start) + len(start)]
        tail = src[src.index(end):]
        src = f"{head}\n{fn()}\n{tail}"
    open(path, "w").write(src)
    return path
