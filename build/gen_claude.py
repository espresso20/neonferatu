"""Claude Code custom theme: ~/.claude/themes/<slug>.json, base dark + overrides.

Only keys present in the built-in dark theme are honoured by the CLI; anything
else is silently dropped, so this list mirrors that key set exactly.
"""
import json, os
import color
from palette import load

def build(dist):
    p = load()
    bg, fg, n, t, crt = p["bg"], p["fg"], p["neon"], p["terminal"], p["crt"]
    # Claude Code draws on the terminal, so its surfaces follow the glass,
    # not the editor void.

    o = {
        # modes and the borders that announce them
        "autoAccept":        n["hex"],
        "autoAcceptShimmer": n["hexLit"],
        "skill":             n["hex"],
        "bashBorder":        n["acid"],
        "planMode":          n["chrome"],
        "permission":        n["sodium"],
        "permissionShimmer": n["sodiumLit"],
        "promptBorder":      n["hex"],
        "promptBorderShimmer": n["hexLit"],
        "ide":               n["coolant"],

        # the assistant itself
        "claude":            n["fang"],
        "claudeShimmer":     n["fangLit"],
        "claudeBlue_FOR_SYSTEM_SPINNER":        n["chrome"],
        "claudeBlueShimmer_FOR_SYSTEM_SPINNER": n["chromeLit"],
        "clawd_body":        n["fang"],
        "clawd_background":  t["background"],

        # text ladder
        "text":              fg["phosphor"],
        "inverseText":       t["background"],
        "inactive":          fg["muted"],
        "inactiveShimmer":   fg["dim"],
        "subtle":            fg["ghost"],
        "suggestion":        n["chrome"],
        "remember":          n["hex"],
        "background":        t["background"],

        # status
        "success":           n["acid"],
        "error":             n["wound"],
        "warning":           n["sodium"],
        "warningShimmer":    n["sodiumLit"],
        "merged":            n["hex"],

        # diffs — these are block backgrounds, not text
        "diffAdded":         color.mix(n["acid"], crt["glass"], 0.72),
        "diffAddedWord":     color.mix(n["acid"], crt["glass"], 0.46),
        "diffAddedDimmed":   color.mix(n["acid"], fg["ghost"], 0.55),
        "diffRemoved":       color.mix(n["wound"], crt["glass"], 0.58),
        "diffRemovedWord":   color.mix(n["wound"], crt["glass"], 0.26),
        "diffRemovedDimmed": color.mix(n["wound"], fg["ghost"], 0.55),

        # subagent identity colors
        "red_FOR_SUBAGENTS_ONLY":    n["wound"],
        "blue_FOR_SUBAGENTS_ONLY":   n["coolant"],
        "green_FOR_SUBAGENTS_ONLY":  n["acid"],
        "yellow_FOR_SUBAGENTS_ONLY": n["sodium"],
        "purple_FOR_SUBAGENTS_ONLY": n["hex"],
        "orange_FOR_SUBAGENTS_ONLY": n["sodiumLit"],
        "pink_FOR_SUBAGENTS_ONLY":   n["fang"],
        "cyan_FOR_SUBAGENTS_ONLY":   n["chrome"],
        "professionalBlue":          n["coolant"],
        "chromeYellow":              n["sodium"],

        # message surfaces
        "userMessageBackground":       p["crt"]["surface"],
        "userMessageBackgroundHover":  p["crt"]["surfaceHi"],
        "composerSidebarBackground":   p["crt"]["glassLit"],
        "selectionBg":                 t["selection"],
        "bashMessageBackgroundColor":  color.mix(crt["surface"], crt["glass"], 0.35),
        "memoryBackgroundColor":       color.mix(n["hex"], bg["void"], 0.86),

        # meters and modes
        "rate_limit_fill":   n["fangLit"],
        "rate_limit_empty":  color.mix(n["fang"], bg["void"], 0.80),
        "fastMode":          n["sodium"],
        "fastModeShimmer":   n["sodiumLit"],
        "effortUltra":       n["hex"],
        "briefLabelYou":     n["chrome"],
        "briefLabelClaude":  n["fang"],

        # spinner rainbow, walked around the neon wheel
        "rainbow_red":     n["wound"],
        "rainbow_orange":  n["sodium"],
        "rainbow_yellow":  n["sodiumLit"],
        "rainbow_green":   n["acid"],
        "rainbow_blue":    n["chrome"],
        "rainbow_indigo":  n["coolant"],
        "rainbow_violet":  n["hex"],
        "rainbow_red_shimmer":    n["woundLit"],
        "rainbow_orange_shimmer": n["sodiumLit"],
        "rainbow_yellow_shimmer": color.mix(n["sodiumLit"], fg["hot"], 0.45),
        "rainbow_green_shimmer":  n["acidLit"],
        "rainbow_blue_shimmer":   n["chromeLit"],
        "rainbow_indigo_shimmer": n["coolantLit"],
        "rainbow_violet_shimmer": n["hexLit"],
    }

    theme = {"name": p["name"], "base": "dark", "overrides": o}
    d = os.path.join(dist, "claude-code")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f'{p["slug"]}.json')
    with open(path, "w") as f:
        json.dump(theme, f, indent=2)
        f.write("\n")
    return path
