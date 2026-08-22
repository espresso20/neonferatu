#!/usr/bin/env python3
"""Generate web/index.html from palette.json.

The site is themed BY the theme: every color on the page comes from the same
palette the editors get, and the readout numbers are measured at build time.
Hand-editing web/index.html puts the site out of step with the product it is
advertising — change palette.json and rebuild instead.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import color
from palette import ROOT, variants

OUT = os.path.join(ROOT, "web")

VARS = [
    ("void", "bg.void"), ("crypt", "bg.crypt"), ("panel", "bg.panel"),
    ("raised", "bg.raised"), ("border", "bg.border"), ("overlay", "bg.overlay"),
    ("fg", "fg.phosphor"), ("hot", "fg.hot"), ("dim", "fg.dim"),
    ("muted", "fg.muted"), ("ghost", "fg.ghost"),
    ("fang", "neon.fang"), ("chrome", "neon.chrome"), ("hex", "neon.hex"),
    ("acid", "neon.acid"), ("sodium", "neon.sodium"), ("wound", "neon.wound"),
    ("coolant", "neon.coolant"),
    ("glass", "crt.glass"), ("glassLit", "crt.glassLit"),
    ("termFg", "terminal.foreground"), ("cursor", "terminal.cursor"),
]

# Ordered as the syntax hierarchy, so the table teaches it on the way past.
READOUT = [
    ("neon.fang",   "keywords, cursor"),
    ("neon.chrome", "functions, links"),
    ("neon.hex",    "types, classes"),
    ("neon.acid",   "strings"),
    ("neon.sodium", "numbers, constants"),
    ("neon.wound",  "errors, deletions"),
    ("fg.phosphor", "body text"),
    ("fg.muted",    "comments"),
    ("bg.void",     "editor background"),
]

TUBE_LABELS = {
    "base":     ("NEON", "night",  "Violet-black editors, glass-green terminals."),
    "phosphor": ("P1",   "green",  "Lights out. One magenta wire still live."),
    "amber":    ("P3",   "amber",  "The other classic tube."),
}

SAMPLE = [
    ("cm", "# the ceiling on how saturated this hue gets, at this lightness\n"),
    ("kw", "def "), ("fn", "max_chroma"), (None, "("), ("pa", "L"), (None, ": "), ("ty", "float"),
    (None, ", "), ("pa", "H"), (None, ": "), ("ty", "float"), (None, ") -> "), ("ty", "float"), (None, ":\n"),
    (None, "    "), ("st", '"""Walk chroma down until the color fits in sRGB."""'), (None, "\n"),
    (None, "    "), ("va", "lo"), (None, ", "), ("va", "hi"), (None, " = "), ("nu", "0.0"), (None, ", "), ("nu", "0.5"), (None, "\n"),
    (None, "    "), ("kw", "for "), ("va", "_"), ("kw", " in "), ("fn", "range"), (None, "("), ("nu", "48"), (None, "):\n"),
    (None, "        "), ("va", "mid"), (None, " = ("), ("va", "lo"), (None, " + "), ("va", "hi"), (None, ") / "), ("nu", "2"), (None, "\n"),
    (None, "        "), ("kw", "if "), ("fn", "in_gamut"), (None, "("), ("pa", "L"), (None, ", "), ("va", "mid"), (None, ", "), ("pa", "H"), (None, "):\n"),
    (None, "            "), ("va", "lo"), (None, " = "), ("va", "mid"), (None, "\n"),
    (None, "        "), ("kw", "else"), (None, ":\n"),
    (None, "            "), ("va", "hi"), (None, " = "), ("va", "mid"), (None, "\n"),
    (None, "    "), ("kw", "return "), ("va", "lo"), (None, "\n"),
]

TERM = [
    ("p", "~/code/neonferatu"), (None, " "), ("c", "$"), (None, " python3 build/build.py\n"),
    ("ok", "palette check ok"), ("d", " — 3 variants, contrast floors, accent\n"),
    ("d", "separation, ramp, no raw hex\n"),
    ("d", "Neonferatu          v1.0.0 — 8 files → dist/\n"),
    ("d", "Neonferatu Amber    v1.0.0 — 8 files → dist/variants/amber/\n"),
    ("d", "Neonferatu Phosphor v1.0.0 — 8 files → dist/variants/phosphor/\n"),
    (None, "\n"),
    ("p", "~/code/neonferatu"), (None, " "), ("c", "$"), (None, " ./install.py\n"),
    ("ok", "  ✔"), ("d", " Monaspace Krypton\n"),
    ("ok", "  ✔"), ("d", " ~/.claude/themes/neonferatu.json\n"),
    ("ok", "  ✔"), ("d", " VS Code extension + settings\n"),
    ("ok", "  ✔"), ("d", " iTerm2 dynamic profile — live, no restart\n"),
    (None, "\n"),
    ("p", "~/code/neonferatu"), (None, " "), ("c", "$"), (None, " "), ("cur", "█"),
]

TARGETS = [
    ("font",     "Monaspace Krypton, weight 500 in editors, bold in terminals"),
    ("claude",   "all 72 theme keys, spinner rainbow and diff blocks included"),
    ("vscode",   "local extension, 1.55 line height, 3px phase-blinking cursor"),
    ("iterm",    "dynamic profile — iTerm2 picks it up live, no restart"),
    ("terminal", "installs the profile and makes it default"),
    ("zed",      "~/.config/zed/themes, Cmd+K Cmd+T to pick"),
    ("sublime",  "tmTheme, same colors"),
    ("bat",      "syntax highlighting in your pager"),
]


def get(pal, path):
    node = pal
    for part in path.split("."):
        node = node[part]
    return node


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def tokens(pairs):
    return "".join(t if c is None else f'<span class="t-{c}">{esc(t)}</span>'
                   for c, t in pairs)


def build(_dist=None):
    os.makedirs(OUT, exist_ok=True)
    vs = list(variants())
    path_to_var = {p: k for k, p in VARS}

    tube_css, metrics, order = [], {}, []
    for vname, pal in vs:
        slug = vname or "base"
        order.append(slug)
        decls = "".join(f"  --{k}: {get(pal, path)};\n" for k, path in VARS)
        sel = ':root, [data-tube="base"]' if slug == "base" else f'[data-tube="{slug}"]'
        tube_css.append(f"{sel} {{\n{decls}}}")
        metrics[slug] = {
            "name": pal["name"],
            "rows": [{
                "hex": get(pal, p),
                "L": f"{color.to_oklch(get(pal, p))[0]:.1f}",
                "C": f"{color.to_oklch(get(pal, p))[1]:.3f}",
                "H": f"{color.to_oklch(get(pal, p))[2]:.0f}",
                "ratio": f"{color.contrast(get(pal, p), get(pal, 'bg.void')):.2f}",
            } for p, _ in READOUT],
        }

    order = ["base"] + [s for s in order if s != "base"]
    switch = "".join(
        '<button class="tube" role="radio" data-set="{s}" aria-checked="{a}" '
        'title="{t}"><span class="tube-code">{c}</span>'
        '<span class="tube-name">{n}</span></button>'.format(
            s=s, a="true" if s == "base" else "false",
            c=TUBE_LABELS.get(s, (s.upper(), "", ""))[0],
            n=TUBE_LABELS.get(s, ("", s, ""))[1],
            t=TUBE_LABELS.get(s, ("", "", ""))[2])
        for s in order)

    rows = "".join(
        '<tr><td class="sw"><i style="background:var(--{v})"></i></td>'
        '<td class="key">{p}</td><td class="role">{r}</td>'
        '<td class="hx" data-f="hex"></td><td class="num" data-f="L"></td>'
        '<td class="num" data-f="C"></td><td class="num" data-f="H"></td>'
        '<td class="num ratio" data-f="ratio"></td></tr>'.format(
            v=path_to_var.get(p, "fg"), p=p, r=role)
        for p, role in READOUT)

    targets = "".join(
        f'<div class="tg"><code>{t}</code><p>{d}</p></div>' for t, d in TARGETS)

    html = TEMPLATE
    for marker, value in (
        ("/*__TUBES__*/", "\n".join(tube_css)),
        ("<!--__SWITCH__-->", switch),
        ("<!--__ROWS__-->", rows),
        ("<!--__TARGETS__-->", targets),
        ("<!--__SAMPLE__-->", tokens(SAMPLE)),
        ("<!--__TERM__-->", tokens(TERM)),
        ("/*__METRICS__*/", json.dumps(metrics, separators=(",", ":"))),
    ):
        html = html.replace(marker, value)

    out = os.path.join(OUT, "index.html")
    with open(out, "w") as f:
        f.write(html)
    return out


TEMPLATE = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "web_template.html")).read()

if __name__ == "__main__":
    print(build())
