#!/usr/bin/env python3
"""Regenerate every theme file in dist/ from palette.json. One source, many editors."""
import os, sys, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from palette import ROOT, load, set_active, variants
import gen_vscode, gen_claude, gen_terminals, gen_extras, gen_web, gen_web_mobile, gen_docs, check

DIST = os.path.join(ROOT, "dist")

# Terminal.app wants a PostScript name, not a family name. Falls back to Meslo
# if the fancier font never got installed.
FONT_PS_CANDIDATES = [load()["font"]["postscript"], load()["font"]["postscriptFallback"]]

def font_postscript():
    try:
        import subprocess
        out = subprocess.run(
            ["system_profiler", "-json", "SPFontsDataType"],
            capture_output=True, text=True, timeout=60).stdout
        for c in FONT_PS_CANDIDATES:
            if f'"{c}"' in out:
                return c
    except Exception:
        pass
    return FONT_PS_CANDIDATES[-1]

def main():
    # Guard rails first. Generating eight formats of a broken palette just gives
    # you eight broken files and a green checkmark.
    if check.main() != 0:
        return 1
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)
    ps = font_postscript()
    for vname, pal in variants():
        set_active(pal)
        out = DIST if not vname else os.path.join(DIST, "variants", vname)
        os.makedirs(out, exist_ok=True)
        made = [
            gen_vscode.build(out),
            gen_claude.build(out),
            gen_terminals.build_iterm(out),
            gen_terminals.build_iterm_dynamic(out),
            gen_terminals.build_live_script(out),
            gen_terminals.build_terminal_app(out, ps),
            gen_extras.build_zed(out),
            gen_extras.build_tmtheme(out),
        ]
        print(f"{pal['name']} v{pal['version']} — {len(made)} files → {os.path.relpath(out, ROOT)}/")
    # The site is generated last, from the base palette plus every variant, so
    # its swatches and its numbers cannot drift from what actually ships.
    set_active(None)
    print(f"web/index.html + web/m/ — generated from {len(list(variants()))} palettes")
    gen_web.build()
    gen_web_mobile.build()
    gen_docs.build()
    return 0

if __name__ == "__main__":
    sys.exit(main())
