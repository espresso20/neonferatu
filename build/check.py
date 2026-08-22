#!/usr/bin/env python3
"""Palette guard rails. Run by build.py; fails the build rather than warning,
because a warning in a build that prints eight OK lines is a warning nobody reads.

Every rule here exists because we shipped the bug it catches.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import color
from palette import ROOT, variants, base_palette

# text on a background needs 4.5:1 for AA. Comments and disabled text are
# deliberately quieter, so they get their own floor.
CONTRAST_FLOORS = [
    ("fg.phosphor", "bg.void",  7.0),
    ("fg.dim",      "bg.void",  4.5),
    ("fg.muted",    "bg.void",  4.5),
    ("fg.ghost",    "bg.void",  2.0),
    ("neon.fang",   "bg.void",  4.5),
    ("neon.chrome", "bg.void",  4.5),
    ("neon.hex",    "bg.void",  4.5),
    ("neon.acid",   "bg.void",  4.5),
    ("neon.sodium", "bg.void",  4.5),
    ("neon.wound",  "bg.void",  4.5),
    ("terminal.foreground", "terminal.background", 7.0),
]

# Syntax colors that sit next to each other in the same line of code. Below this
# they stop being distinguishable in a wall of text — fang and wound shipped at
# 0.055 for a year and errors were invisible inside keywords.
ACCENTS = ["fang", "chrome", "hex", "acid", "sodium", "wound", "coolant"]
MIN_DISTANCE = 0.10

# On a monochrome ladder every accent shares one hue, so separation is a
# lightness question. 6 L* is about where two greens stop swapping in a diff.
MIN_MONO_LIGHTNESS = 6.0

BG_RAMP = ["void", "crypt", "panel", "raised", "border", "overlay"]

GEN_DIR = os.path.join(ROOT, "build")
# 8-digit hex ending in 00/80 etc is an alpha value, not a color choice.
HEX_LITERAL = re.compile(r'"#(?:[0-9A-Fa-f]{6})"')


def _get(pal, path):
    node = pal
    for part in path.split("."):
        node = node[part]
    return node


def check_palette(vname, pal):
    fails = []
    tag = vname or "base"

    for fg_key, bg_key, floor in CONTRAST_FLOORS:
        try:
            fg, bg = _get(pal, fg_key), _get(pal, bg_key)
        except KeyError:
            continue
        ratio = color.contrast(fg, bg)
        if ratio < floor:
            fails.append(f"[{tag}] {fg_key} on {bg_key} is {ratio:.2f}:1, floor is {floor}")

    present = [a for a in ACCENTS if a in pal["neon"]]
    anchor = pal.get("anchorHue")
    mono = pal.get("mode") == "mono" and anchor is not None

    def on_anchor(key):
        """True if this accent belongs to the monochrome ladder rather than
        being one of the chromatic wires kept live on top of it."""
        if not mono:
            return False
        return color.hue_gap(pal["neon"][key], color.from_oklch(70.0, 0.10, anchor)) <= 15.0

    for i, a in enumerate(present):
        for b in present[i + 1:]:
            # A mono variant deliberately runs several accents on one hue and
            # separates them by value instead. Measuring hue distance there
            # would reject a correct green-screen theme, so the ladder gets
            # judged on lightness and everything else stays on distance.
            if on_anchor(a) and on_anchor(b):
                gap = abs(color.to_oklch(pal["neon"][a])[0] - color.to_oklch(pal["neon"][b])[0])
                if gap < MIN_MONO_LIGHTNESS:
                    fails.append(
                        f"[{tag}] neon.{a} and neon.{b} sit {gap:.1f} L apart on the "
                        f"anchor hue (min {MIN_MONO_LIGHTNESS}) — the ladder collapses")
                continue
            d = color.distance(pal["neon"][a], pal["neon"][b])
            if d < MIN_DISTANCE:
                fails.append(
                    f"[{tag}] neon.{a} and neon.{b} are {d:.3f} apart "
                    f"(min {MIN_DISTANCE}) — they will read as the same color")

    ramp = [color.to_oklch(pal["bg"][k])[0] for k in BG_RAMP if k in pal["bg"]]
    for i in range(len(ramp) - 1):
        if ramp[i + 1] <= ramp[i]:
            fails.append(
                f"[{tag}] bg ramp is not monotonic: {BG_RAMP[i]} L{ramp[i]:.1f} "
                f">= {BG_RAMP[i+1]} L{ramp[i+1]:.1f}")

    # Hue is meaningless on a near-black: bg.void is #06050F, where 8-bit
    # rounding moves the measured angle more than any design decision does.
    # Only judge drift on steps carrying enough chroma to have a hue at all.
    hues = [h for h, C in
            ((color.to_oklch(pal["bg"][k])[2], color.to_oklch(pal["bg"][k])[1])
             for k in BG_RAMP if k in pal["bg"]) if C >= 0.03]
    if len(hues) >= 2:
        spread = max(hues) - min(hues)
        if spread > 6.0:
            fails.append(f"[{tag}] bg ramp hue drifts {spread:.1f} degrees; keep it under 6")

    return fails


def check_generators():
    """No raw color literals in generators. Colors come from the palette or from
    a mix() of palette entries, so that a variant can actually move them."""
    fails = []
    for fn in sorted(os.listdir(GEN_DIR)):
        if not fn.startswith("gen_") or not fn.endswith(".py"):
            continue
        path = os.path.join(GEN_DIR, fn)
        for i, line in enumerate(open(path), 1):
            if "check:allow-hex" in line:
                continue
            for m in HEX_LITERAL.finditer(line):
                fails.append(f"[generators] {fn}:{i} hardcoded {m.group(0)} — derive it from the palette")
    return fails


def main():
    fails = []
    for vname, pal in variants():
        fails += check_palette(vname, pal)
    fails += check_generators()

    if fails:
        print("\npalette check FAILED:", file=sys.stderr)
        for f in fails:
            print(f"  x {f}", file=sys.stderr)
        print(f"\n{len(fails)} problem(s).\n", file=sys.stderr)
        return 1
    n = len(list(variants()))
    print(f"palette check ok — {n} variant(s), contrast floors, accent separation, ramp, no raw hex")
    return 0


if __name__ == "__main__":
    sys.exit(main())
