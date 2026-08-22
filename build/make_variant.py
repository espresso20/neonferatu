#!/usr/bin/env python3
"""Generate the monochrome variants.

A mono tube runs one hue and builds its syntax hierarchy out of lightness
instead. Adding another is one line in TUBES — pick an anchor hue and the
ladder, backgrounds, foregrounds and terminal all fall out of it.

    python3 build/make_variant.py && python3 build/build.py
"""
import sys, os, json, collections
ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, 'build'))
import color as c
from palette import base_palette

base = base_palette()

def mono(name, slug, blurb, anchor):
    """One anchor hue; hierarchy by lightness instead of hue. Fully derived, so
    a new tube is this call and nothing else."""
    def at(L, pull=1.0):
        return c.from_oklch(L, c.max_chroma(L, anchor) * pull, anchor)

    v = collections.OrderedDict()
    v['name'], v['slug'], v['blurb'] = name, slug, blurb
    v['mode'] = 'mono'
    v['anchorHue'] = anchor

    # backgrounds keep the family's lightness ladder; only the hue moves.
    # phosphor used to float 4 points brighter than base, so the two variants
    # never shared a perceived depth.
    v['bg'] = collections.OrderedDict(
        (k, at(c.to_oklch(base['bg'][k])[0], 0.55)) for k in base['bg'])

    v['fg'] = collections.OrderedDict([
        ('phosphor', at(89.0, 0.62)),
        ('hot',      at(96.0, 0.30)),
        ('dim',      at(73.0, 0.72)),
        ('muted',    at(60.0, 0.70)),   # lifted until it clears AA
        ('ghost',    at(45.0, 0.70)),
    ])

    # The syntax ladder. Rungs spread across whatever lightness range this
    # anchor can actually use: amber runs out of contrast against a near-black
    # far sooner than green does, so a hardcoded 64/72/80/88 fits one tube and
    # collapses the other. Find the floor, then divide evenly.
    void = v['bg']['void']
    floor = 50.0
    while floor < 88.0 and c.contrast(at(floor), void) < 4.6:
        floor += 0.5

    # Numbers keep the P3 amber wire — it is off-anchor, so it reads as its own
    # thing without spending a rung. Unless the tube IS amber, where that says
    # nothing and numbers have to join the ladder.
    amber_anchored = min(abs(anchor - 76.4), 360 - abs(anchor - 76.4)) <= 25.0
    count = 5 if amber_anchored else 4
    rungs = [floor + (88.0 - floor) * i / (count - 1) for i in range(count)]
    step = rungs[1] - rungs[0]
    ladder = list(rungs)

    entries = []
    if amber_anchored:
        entries += [('sodium', at(ladder.pop(0))),
                    ('sodiumLit', at(min(rungs[0] + step, 94.0), 0.90))]
    else:
        entries += [('sodium', '@crt.p3Amber'),
                    ('sodiumLit', '@shift(crt.p3Amber, 9)')]
    for key, L in zip(('hex', 'coolant', 'chrome', 'acid'), ladder):
        entries.append((key, at(L)))
        lit = 94.0 if key == 'acid' else min(L + step, 92.0)
        entries.append((key + 'Lit', at(lit, 0.60 if key == 'acid' else 0.88)))
    v['neon'] = collections.OrderedDict(entries)
    # fang / wound inherit from base: the one live magenta wire.

    v['crt'] = collections.OrderedDict([
        ('glass',     at(c.to_oklch(base['bg']['void'])[0], 0.55)),
        ('glassLit',  at(c.to_oklch(base['bg']['crypt'])[0], 0.55)),
        ('surface',   at(c.to_oklch(base['bg']['panel'])[0], 0.55)),
        ('surfaceHi', at(c.to_oklch(base['bg']['raised'])[0], 0.55)),
        ('p1',        at(88.0)),
        ('p1Dim',     at(66.0)),
        ('p1Glow',    at(92.0, 0.70)),
        ('p1Pale',    at(96.0, 0.35)),
    ])
    v['terminal'] = collections.OrderedDict([
        ('foreground', '@crt.p1'),
        ('cursor',     '@crt.p1Glow'),
    ])
    return v

TUBES = [
    ('variants/phosphor.json', 'Neonferatu Phosphor', 'neonferatu-phosphor',
     'Neonferatu with the lights off and a P1 tube warmed up. Green screen, one magenta wire still live.', 150.0),
    ('variants/amber.json', 'Neonferatu Amber', 'neonferatu-amber',
     'The other classic tube. P3 amber all the way down, magenta still humming underneath.', 78.0),
]

for fn, name, slug, blurb, anchor in TUBES:
    json.dump(mono(name, slug, blurb, anchor), open(fn, 'w'), indent=2)
    open(fn, 'a').write('\n')
    print('wrote', fn)
