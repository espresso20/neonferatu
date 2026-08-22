"""Load palette.json (optionally patched by a variant) and expose flat helpers."""
import copy, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import color

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ACTIVE = None

def deep_merge(base, patch):
    out = copy.deepcopy(base)
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out

def base_palette():
    """Raw palette, references intact. Use load() unless you need the source form."""
    with open(os.path.join(ROOT, "palette.json")) as f:
        return json.load(f)

def set_active(pal):
    """Generators call load(); build.py swaps what that returns per variant."""
    global _ACTIVE
    _ACTIVE = pal

def load():
    return _ACTIVE if _ACTIVE is not None else resolve(base_palette())

def variants():
    """Every variants/*.json, merged over the base. Base is always first."""
    out = [("", resolve(base_palette()))]
    vdir = os.path.join(ROOT, "variants")
    if os.path.isdir(vdir):
        for name in sorted(os.listdir(vdir)):
            if not name.endswith(".json"):
                continue
            with open(os.path.join(vdir, name)) as f:
                # merge first, resolve second: a variant that overrides neon.fang
                # automatically drags ansi.magenta and the cursor along with it.
                out.append((name[:-5], resolve(deep_merge(base_palette(), json.load(f)))))
    return out

# ---------------------------------------------------------------- references
# A palette where `ansi.magenta` is a literal copy of `neon.fang` is a palette
# that drifts the moment you retune an accent — which is exactly what happened.
# Derived values are written as references and resolved at load time, so a color
# still only ever exists in one place.
#
#   "@neon.fang"                     -> that color
#   "@mix(neon.acid, bg.void, 0.18)" -> perceptual blend, for diff backgrounds
#   "@alpha(neon.fang, 40)"          -> #RRGGBBAA
#   "@shift(neon.fang, 9)"           -> same hue, lightness +9

_REF = re.compile(r'^@(?:(\w+)\((.*)\)|([\w.]+))$')

def _lookup(pal, path):
    node = pal
    for part in path.strip().split('.'):
        node = node[part]
    if isinstance(node, str) and node.startswith('@'):
        return _eval(pal, node)
    return node

def _eval(pal, expr):
    m = _REF.match(expr.strip())
    if not m:
        raise ValueError(f'bad palette reference: {expr!r}')
    fn, rawargs, plain = m.groups()
    if plain:
        return _lookup(pal, plain)
    args = [a.strip() for a in rawargs.split(',')]
    if fn == 'mix':
        return color.mix(_lookup(pal, args[0]), _lookup(pal, args[1]), float(args[2]))
    if fn == 'alpha':
        return color.alpha(_lookup(pal, args[0]), float(args[1]))
    if fn == 'shift':
        c0 = _lookup(pal, args[0])
        L, C, H = color.to_oklch(c0)
        L2 = max(0.0, min(100.0, L + float(args[1])))
        return color.from_oklch(L2, min(C, color.max_chroma(L2, H)), H)
    raise ValueError(f'unknown palette function: {fn}')

def resolve(pal):
    """Replace every @reference with a concrete hex, depth-first."""
    def walk(node):
        if isinstance(node, dict):
            return {k: walk(v) for k, v in node.items()}
        if isinstance(node, list):
            return [walk(v) for v in node]
        if isinstance(node, str) and node.startswith('@'):
            return _eval(pal, node)
        return node
    return walk(pal)

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def hex_to_floats(h):
    return tuple(c / 255.0 for c in hex_to_rgb(h))

def rgb_css(h):
    r, g, b = hex_to_rgb(h)
    return f"rgb({r},{g},{b})"

def alpha(h, pct):
    """#RRGGBB + opacity percent -> #RRGGBBAA, for editors that take 8-digit hex."""
    return h + format(round(255 * pct / 100), "02x")
