#!/usr/bin/env python3
"""Generate web/m/index.html — the phone build of the site.

Same palette, same numbers, different shape. The desktop page puts the readout
in an eight-column table with a 660px floor, which on a phone is a sideways
scroll of the most important thing on the page. Here it is a stack of cards.

Generated alongside the desktop page by build.py, from the same palette, so the
two cannot disagree about a colour.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import color
from palette import ROOT, variants
from gen_web import VARS, READOUT, TUBE_LABELS, TARGETS, SAMPLE, tokens, get

OUT = os.path.join(ROOT, "web", "m")


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
        metrics[slug] = {"rows": [{
            "hex": get(pal, p),
            "L": f"{color.to_oklch(get(pal, p))[0]:.0f}",
            "C": f"{color.to_oklch(get(pal, p))[1]:.3f}",
            "ratio": f"{color.contrast(get(pal, p), get(pal, 'bg.void')):.1f}",
        } for p, _ in READOUT]}

    order = ["base"] + [s for s in order if s != "base"]
    switch = "".join(
        '<button class="tube" data-set="{s}" role="radio" aria-checked="{a}">{c}</button>'.format(
            s=s, a="true" if s == "base" else "false",
            c=TUBE_LABELS.get(s, (s.upper(), "", ""))[0])
        for s in order)

    cards = ""
    for p, role in READOUT:
        v = path_to_var.get(p, "fg")
        cards += (
            f'<li class="sw"><i style="background:var(--{v})"></i>'
            f'<div class="sw-body"><b>{p}</b><span>{role}</span></div>'
            f'<div class="sw-num"><code data-f="hex"></code>'
            f'<em>L<span data-f="L"></span> · C<span data-f="C"></span> · '
            f'<span data-f="ratio"></span>:1</em></div></li>')

    targets = "".join(f'<li><code>{t}</code><span>{d}</span></li>' for t, d in TARGETS)

    html = TEMPLATE
    for marker, value in (
        ("/*__TUBES__*/", "\n".join(tube_css)),
        ("<!--__SWITCH__-->", switch),
        ("<!--__CARDS__-->", cards),
        ("<!--__TARGETS__-->", targets),
        ("<!--__SAMPLE__-->", tokens(SAMPLE)),
        ("/*__METRICS__*/", json.dumps(metrics, separators=(",", ":"))),
    ):
        html = html.replace(marker, value)

    out = os.path.join(OUT, "index.html")
    with open(out, "w") as f:
        f.write(html)
    return out


TEMPLATE = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "web_mobile_template.html")).read()

if __name__ == "__main__":
    print(build())
