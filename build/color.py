"""OKLCH color math. Zero dependencies, because a theme generator that needs a
virtualenv is a theme nobody installs.

Everything the palette does — picking accents at equal weight, mixing a diff
background out of a foreground, proving two colors are far enough apart — is a
lightness or chroma operation, and sRGB is bad at both. So we do the work in
OKLab/OKLCH and only convert back to hex at the very end.
"""
import math

# ---------------------------------------------------------------- sRGB <-> linear

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return "#" + "".join(format(max(0, min(255, round(c * 255))), "02X") for c in rgb)

def _to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def _from_linear(c):
    return c * 12.92 if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055

# ---------------------------------------------------------------- OKLab

def _linear_to_oklab(r, g, b):
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = (math.copysign(abs(x) ** (1 / 3), x) for x in (l, m, s))
    return (
        0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
        1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
        0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s,
    )

def _oklab_to_linear(L, a, b):
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (
        +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )

# ---------------------------------------------------------------- OKLCH (L is 0-100)

def to_oklch(hex_str):
    r, g, b = (_to_linear(c) for c in hex_to_rgb(hex_str))
    L, a, bb = _linear_to_oklab(r, g, b)
    return (L * 100.0, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360.0)

def _oklch_to_linear(L, C, H):
    rad = math.radians(H)
    return _oklab_to_linear(L / 100.0, C * math.cos(rad), C * math.sin(rad))

def in_gamut(L, C, H, eps=1e-4):
    return all(-eps <= c <= 1 + eps for c in _oklch_to_linear(L, C, H))

def from_oklch(L, C, H):
    """OKLCH -> hex, reducing chroma until the color fits in sRGB.

    Clipping RGB directly is the common shortcut and it shifts hue visibly on
    saturated colors — exactly the ones we care about. Walking chroma down holds
    the hue and the lightness, which is the whole point of working here.
    """
    if not in_gamut(L, C, H):
        lo, hi = 0.0, C
        for _ in range(48):
            mid = (lo + hi) / 2
            if in_gamut(L, mid, H):
                lo = mid
            else:
                hi = mid
        C = lo
    lin = _oklch_to_linear(L, C, H)
    return rgb_to_hex(tuple(_from_linear(max(0.0, min(1.0, c))) for c in lin))

def max_chroma(L, H):
    """The most saturated this hue gets at this lightness, inside sRGB."""
    lo, hi = 0.0, 0.5
    for _ in range(48):
        mid = (lo + hi) / 2
        if in_gamut(L, mid, H):
            lo = mid
        else:
            hi = mid
    return lo

# ---------------------------------------------------------------- operations

def with_lightness(hex_str, L, chroma_scale=1.0):
    """Move a color to a target lightness, holding its hue."""
    _, C, H = to_oklch(hex_str)
    return from_oklch(L, C * chroma_scale, H)

def mix(a, b, t):
    """Blend two colors in OKLab. t=0 -> a, t=1 -> b. Perceptually even, so a
    50% mix actually looks halfway rather than muddy."""
    ra, ga, ba = (_to_linear(c) for c in hex_to_rgb(a))
    rb, gb, bb = (_to_linear(c) for c in hex_to_rgb(b))
    A = _linear_to_oklab(ra, ga, ba)
    B = _linear_to_oklab(rb, gb, bb)
    L, x, y = (A[i] + (B[i] - A[i]) * t for i in range(3))
    lin = _oklab_to_linear(L, x, y)
    return rgb_to_hex(tuple(_from_linear(max(0.0, min(1.0, c))) for c in lin))

def alpha(hex_str, pct):
    """#RRGGBB + opacity percent -> #RRGGBBAA, for editors that take 8-digit hex."""
    return hex_str + format(round(255 * pct / 100), "02X")

# ---------------------------------------------------------------- measurement

def luminance(hex_str):
    r, g, b = (_to_linear(c) for c in hex_to_rgb(hex_str))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast(a, b):
    """WCAG 2.1 contrast ratio, 1.0 to 21.0."""
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)

def distance(a, b):
    """Perceptual distance in OKLab. Two syntax colors under ~0.10 start to read
    as the same color in a wall of text; that's the number check.py enforces."""
    ra, ga, ba = (_to_linear(c) for c in hex_to_rgb(a))
    rb, gb, bb = (_to_linear(c) for c in hex_to_rgb(b))
    A = _linear_to_oklab(ra, ga, ba)
    B = _linear_to_oklab(rb, gb, bb)
    return math.sqrt(sum((A[i] - B[i]) ** 2 for i in range(3)))

def hue_gap(a, b):
    """Smallest angle between two hues, in degrees."""
    d = abs(to_oklch(a)[2] - to_oklch(b)[2]) % 360.0
    return min(d, 360.0 - d)
