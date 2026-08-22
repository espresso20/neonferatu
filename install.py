#!/usr/bin/env python3
"""Install Neonferatu into every app that will have it.

Every file this touches is backed up to backups/<timestamp>/ first.

  ./install.py                        everything, base theme
  ./install.py claude vscode          only those targets
  ./install.py --variant phosphor     the green-CRT variant instead

Variants install side by side, so running it once per variant leaves both
available in every app and activates whichever you ran last.
"""
import json, os, plistlib, shutil, subprocess, sys, time

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
HOME = os.path.expanduser("~")
STAMP = time.strftime("%Y%m%d-%H%M%S")
BACKUP = os.path.join(ROOT, "backups", STAMP)

if not os.path.isdir(DIST):
    subprocess.run([sys.executable, os.path.join(ROOT, "build", "build.py")], check=True)

VARIANT = ""
for i, a in enumerate(sys.argv):
    if a == "--variant" and i + 1 < len(sys.argv):
        VARIANT = sys.argv[i + 1]
    elif a.startswith("--variant="):
        VARIANT = a.split("=", 1)[1]
if VARIANT:
    DIST = os.path.join(DIST, "variants", VARIANT)
    if not os.path.isdir(DIST):
        have = os.path.join(ROOT, "dist", "variants")
        opts = ", ".join(sorted(os.listdir(have))) if os.path.isdir(have) else "none built"
        sys.exit(f"no such variant: {VARIANT}\navailable: {opts}")

sys.path.insert(0, os.path.join(ROOT, "build"))
from palette import base_palette, deep_merge  # noqa: E402
PAL = base_palette()
if VARIANT:
    with open(os.path.join(ROOT, "variants", f"{VARIANT}.json")) as _f:
        PAL = deep_merge(PAL, json.load(_f))
SLUG, NAME = PAL["slug"], PAL["name"]
FONT = PAL["font"]

ok, warn, skip = [], [], []
def _ok(m): ok.append(m); print(f"  \033[38;2;156;255;46m✔\033[0m {m}")
def _warn(m): warn.append(m); print(f"  \033[38;2;255;182;39m!\033[0m {m}")
def _skip(m): skip.append(m); print(f"  \033[38;2;107;99;150m·\033[0m {m}")

def backup(path):
    if not os.path.exists(path):
        return
    dest = os.path.join(BACKUP, path.replace(HOME, "home").lstrip("/"))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    (shutil.copytree if os.path.isdir(path) else shutil.copy2)(path, dest)

def patch_json(path, updates):
    """Merge keys into a JSON settings file, preserving everything else."""
    backup(path)
    data = {}
    if os.path.exists(path):
        with open(path) as f:
            txt = f.read().strip()
        if txt:
            data = json.loads(txt)
    data.update(updates)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

def running(app):
    return subprocess.run(["pgrep", "-x", app], capture_output=True).returncode == 0


# ---------------------------------------------------------------- font ----
def do_font():
    out = subprocess.run(["brew", "list", "--cask"], capture_output=True, text=True).stdout
    if "font-monaspace-nerd-font" in out:
        _skip("font-monaspace-nerd-font already installed")
        return
    print("    installing font-monaspace-nerd-font (this hits the network)...")
    r = subprocess.run(["brew", "install", "--cask", "font-monaspace-nerd-font"],
                       capture_output=True, text=True)
    if r.returncode == 0:
        _ok("installed Monaspace Nerd Font (Krypton is the fat one)")
    else:
        _warn(f"font install failed, falling back to Meslo: {r.stderr.strip()[:120]}")


# -------------------------------------------------------------- claude ----
def do_claude():
    dest_dir = os.path.join(HOME, ".claude", "themes")
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy2(os.path.join(DIST, "claude-code", f"{SLUG}.json"),
                 os.path.join(dest_dir, f"{SLUG}.json"))
    _ok(f"~/.claude/themes/{SLUG}.json")
    patch_json(os.path.join(HOME, ".claude", "settings.json"),
               {"theme": f"custom:{SLUG}"})
    _ok(f'claude settings.json  theme = "custom:{SLUG}"  (restart Claude Code)')


# -------------------------------------------------------------- vscode ----
def do_vscode():
    src = os.path.join(DIST, "vscode", SLUG)
    dest = os.path.join(HOME, ".vscode", "extensions",
                        f"local.{SLUG}-{PAL['version']}")
    if not os.path.isdir(os.path.dirname(dest)):
        _skip("VS Code not found")
        return
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    _ok(f"extension → {dest.replace(HOME, '~')}")

    snippet = json.load(open(os.path.join(DIST, "vscode", "settings-snippet.json")))
    settings = os.path.join(HOME, "Library", "Application Support", "Code",
                            "User", "settings.json")
    # don't force an icon theme the user may not have installed
    existing = {}
    if os.path.exists(settings):
        existing = json.loads(open(settings).read() or "{}")
    if "workbench.iconTheme" not in existing:
        snippet.pop("workbench.iconTheme", None)
    patch_json(settings, snippet)
    _ok("VS Code settings.json patched (theme + fat font + cursor)")
    if running("Electron") or running("Code Helper"):
        _warn("VS Code is running — reload the window (Cmd+Shift+P → Reload Window)")


# --------------------------------------------------------------- iterm ----
ITERM_PLIST = os.path.join(HOME, "Library", "Preferences",
                           "com.googlecode.iterm2.plist")

def do_iterm():
    preset = os.path.join(DIST, "iterm2", f"{SLUG}.itermcolors")
    dynamic = os.path.join(DIST, "iterm2", f"{SLUG}.dynamic-profile.json")
    if not os.path.exists(ITERM_PLIST):
        _skip("iTerm2 not found")
        return

    # Dynamic profiles are picked up live — no restart, no prefs surgery.
    dyn_dir = os.path.join(HOME, "Library", "Application Support", "iTerm2",
                           "DynamicProfiles")
    os.makedirs(dyn_dir, exist_ok=True)
    shutil.copy2(dynamic, os.path.join(dyn_dir, f"{SLUG}.json"))
    _ok(f"iTerm2 profile '{NAME}' installed (appears immediately)")

    if running("iTerm2"):
        subprocess.run(["open", "-a", "iTerm", preset], capture_output=True)
        _warn("iTerm2 is running, so its Default profile was left alone. Either "
              f"Settings → Profiles → {NAME} → Other Actions → Set as Default, "
              "or quit iTerm2 and re-run `./install.py iterm` to repaint every profile")
        _ok(f"repaint this session right now:  {os.path.relpath(os.path.join(DIST, 'iterm2', 'live.sh'), ROOT)}")
        return

    backup(ITERM_PLIST)
    with open(ITERM_PLIST, "rb") as f:
        prefs = plistlib.load(f)
    colors = plistlib.loads(open(preset, "rb").read())
    prefs.setdefault("Custom Color Presets", {})[NAME] = colors

    font = f"{FONT['postscript']} {FONT['termSize']}"
    patched = 0
    for profile in prefs.get("New Bookmarks", []):
        profile.update(colors)
        profile["Normal Font"] = font
        profile["Non Ascii Font"] = font
        profile["Use Non-ASCII Font"] = False
        profile["Horizontal Spacing"] = 1.0
        profile["Vertical Spacing"] = round(FONT["lineHeight"] - 0.35, 2)
        profile["Use Bold Font"] = True
        profile["Use Bright Bold"] = True
        profile["Cursor Type"] = 2
        profile["Blinking Cursor"] = True
        profile["Blur"] = True
        profile["Blur Radius"] = 8.0
        profile["Transparency"] = 0.06
        patched += 1
    with open(ITERM_PLIST, "wb") as f:
        plistlib.dump(prefs, f, fmt=plistlib.FMT_BINARY)
    subprocess.run(["killall", "cfprefsd"], capture_output=True)
    _ok(f"iTerm2: preset applied to {patched} existing profile(s)")


# ------------------------------------------------------------ terminal ----
def do_terminal_app():
    profile_path = os.path.join(DIST, "terminal-app", f"{SLUG}.terminal")
    with open(profile_path, "rb") as f:
        profile = plistlib.load(f)
    export = subprocess.run(["defaults", "export", "com.apple.Terminal", "-"],
                            capture_output=True)
    if export.returncode != 0:
        _skip("Terminal.app preferences unreadable")
        return
    prefs = plistlib.loads(export.stdout)
    os.makedirs(BACKUP, exist_ok=True)
    with open(os.path.join(BACKUP, "com.apple.Terminal.plist"), "wb") as f:
        f.write(export.stdout)

    prefs.setdefault("Window Settings", {})[NAME] = profile
    prefs["Default Window Settings"] = NAME
    prefs["Startup Window Settings"] = NAME
    blob = plistlib.dumps(prefs, fmt=plistlib.FMT_XML)
    r = subprocess.run(["defaults", "import", "com.apple.Terminal", "-"],
                       input=blob, capture_output=True)
    if r.returncode != 0:
        _warn(f"Terminal.app import failed: {r.stderr.decode()[:120]}")
        return
    subprocess.run(["killall", "cfprefsd"], capture_output=True)
    _ok("Terminal.app: profile installed and set as default")
    if running("Terminal"):
        _warn("Terminal.app is running — quit it before it overwrites these prefs")


# ----------------------------------------------------------------- zed ----
def do_zed():
    zed_dir = os.path.join(HOME, ".config", "zed")
    if not os.path.isdir(zed_dir):
        _skip("Zed not found")
        return
    themes = os.path.join(zed_dir, "themes")
    os.makedirs(themes, exist_ok=True)
    shutil.copy2(os.path.join(DIST, "zed", f"{SLUG}.json"),
                 os.path.join(themes, f"{SLUG}.json"))
    _ok(f"~/.config/zed/themes/{SLUG}.json  (Cmd+K Cmd+T → {NAME})")


# ------------------------------------------------- sublime text and bat ----
def do_sublime():
    pkg = os.path.join(HOME, "Library", "Application Support", "Sublime Text",
                       "Packages", "User")
    if not os.path.isdir(os.path.dirname(os.path.dirname(pkg))):
        _skip("Sublime Text not found")
        return
    os.makedirs(pkg, exist_ok=True)
    shutil.copy2(os.path.join(DIST, "tmtheme", f"{SLUG}.tmTheme"),
                 os.path.join(pkg, f"{NAME}.tmTheme"))
    _ok(f"Sublime: Packages/User/{NAME}.tmTheme  (Preferences → Select Color Scheme)")

def do_bat():
    if not shutil.which("bat"):
        _skip("bat not installed")
        return
    cfg = subprocess.run(["bat", "--config-dir"], capture_output=True,
                         text=True).stdout.strip()
    themes = os.path.join(cfg, "themes")
    os.makedirs(themes, exist_ok=True)
    shutil.copy2(os.path.join(DIST, "tmtheme", f"{SLUG}.tmTheme"),
                 os.path.join(themes, f"{NAME}.tmTheme"))
    subprocess.run(["bat", "cache", "--build"], capture_output=True)
    _ok(f'bat: theme cached  (export BAT_THEME="{NAME}")')


TARGETS = {
    "font": do_font, "claude": do_claude, "vscode": do_vscode,
    "iterm": do_iterm, "terminal": do_terminal_app, "zed": do_zed,
    "sublime": do_sublime, "bat": do_bat,
}

def main():
    raw = sys.argv[1:]
    args = [a for i, a in enumerate(raw)
            if not a.startswith("-") and not (i and raw[i - 1] == "--variant")]
    chosen = args or list(TARGETS)
    bad = [a for a in chosen if a not in TARGETS]
    if bad:
        sys.exit(f"unknown target(s): {', '.join(bad)}\nvalid: {', '.join(TARGETS)}")
    print(f"\n\033[38;2;255;46;136m{NAME}\033[0m → {', '.join(chosen)}")
    print(f"backups: {BACKUP.replace(HOME, '~')}\n")
    for t in chosen:
        TARGETS[t]()
    print(f"\n{len(ok)} applied, {len(warn)} need a nudge, {len(skip)} skipped.")
    if warn:
        print("\nnudges:")
        for w in warn:
            print(f"  - {w}")

if __name__ == "__main__":
    main()
