# Neonferatu

A retro-cyberpunk dark theme for the whole toolchain. Phosphor-violet void,
sodium streetlight, and a great deal of hot pink.

Dracula was a good theme in 2013 and it is a beige memory now. This one is ours:
one palette file, one build step, every app we actually use.

```
  ██╗ ██╗ █████╗  ██████╗ ███╗   ██╗    the count is dead,
  ██║ ██║ ██╔══╝ ██╔═══██╗████╗  ██║    we run the city now
  ██╗ ██╗ █████╗ ╚██████╔╝██║ ╚████║
```

## The palette

| role | hex | where it lands |
|---|---|---|
| `bg.void` | `#07050E` | editor + terminal background |
| `bg.crypt` | `#0D0B1A` | sidebars, panels, status bar |
| `bg.panel` | `#131029` | popovers, inputs, menus |
| `bg.raised` | `#1B1638` | selected rows, ANSI black |
| `bg.border` | `#2A2450` | every 1px line in the UI |
| `bg.overlay` | `#382F66` | selection fill |
| `fg.phosphor` | `#E8E3FF` | body text — violet-white, like a tired CRT |
| `fg.dim` | `#A99FD6` | secondary text, punctuation, parameters |
| `fg.muted` | `#6B6396` | comments |
| `fg.ghost` | `#4A4270` | line numbers, disabled |
| `neon.fang` | `#FF2E88` | **keywords**, cursor, active markers, Claude |
| `neon.chrome` | `#00E5FF` | functions, links, properties, plan mode |
| `neon.hex` | `#B14BFF` | types and classes, focus rings, auto-accept |
| `neon.acid` | `#9CFF2E` | strings, success, additions |
| `neon.sodium` | `#FFB627` | numbers, constants, warnings, attributes |
| `neon.wound` | `#FF3864` | errors, deletions |
| `neon.coolant` | `#3B8EFF` | ANSI blue, IDE chrome |
| `crt.glass` | `#07170F` | **terminal background** — unlit tube, bottle green |
| `crt.glassLit` | `#0C2117` | the same glass with the beam on it |
| `crt.p1` | `#33FF66` | P1 phosphor, the classic green |
| `crt.p1Glow` | `#8CFFB0` | **terminal foreground** — pale phosphor |
| `crt.p3Amber` | `#FFB000` | P3 amber, the other classic |

### Green, and how much of it

The editor is a neon-lit night; the **terminal is a CRT**. So they don't share a
background. Editors sit on `bg.void` (`#07050E`, violet-black) and terminals sit on
`crt.glass` (`#07170F`) — the deep bottle green of a monitor that isn't switched on
— with `crt.p1Glow` text. Not lime, not Matrix rain. Just enough green that the
shell feels like hardware.

Claude Code follows the terminal, since that's where it lives: its background,
message surfaces, and selection all come off the glass ramp rather than the
editor's violet.

Each neon has a `*Lit` sibling (`fangLit`, `chromeLit`, …) used for bright ANSI
slots, shimmer animations, and hover states.

The syntax hierarchy is deliberate and short: **magenta = control flow**,
**cyan = things you call**, **violet = things you name**, **green = literal text**,
**amber = literal numbers**. Everything else is grey. If a fifth accent creeps in,
we've lost the plot.

## Variants

| variant | what it is |
|---|---|
| *(base)* | neon night. Violet-black editors, glass-green terminals. |
| `phosphor` | lights out. Everything is P1 green on dark glass, with magenta kept for keywords and the cursor, amber for numbers. A green-screen terminal that happens to run VS Code. |

```bash
./install.py                      # base, activated
./install.py --variant phosphor   # phosphor, activated
```

They install side by side. Run both and every app lists both — VS Code's theme
picker, iTerm2's profile list, `/theme` in Claude Code, `Cmd+K Cmd+T` in Zed —
with whichever you ran last set as active.

Adding another is one file: drop `variants/<name>.json` containing only the keys
you want to change (it deep-merges over `palette.json`), set `name` and `slug`,
and rebuild. An amber P3 variant is about fifteen lines.

## Layout

```
palette.json              the only file you edit to change a color
variants/<name>.json      a patch over palette.json; one per variant
build/                    generators — one per output format
  build.py                run this after touching palette.json
dist/                     generated, disposable, do not hand-edit
dist/variants/<name>/     the same outputs, built from the merged variant
install.py                installs dist/ into every app; backs up first
uninstall.py              restores the newest backup
preview.sh                prints the palette + a syntax sample in your terminal
backups/<timestamp>/      every file install.py touched, before it touched it
```

## Use it

```bash
python3 build/build.py          # regenerate dist/ from palette.json
./install.py                    # everything, including the font
./install.py claude vscode      # or just the targets you want
./preview.sh                    # see what you did
./preview.sh phosphor           # ...in a variant
./uninstall.py                  # put it all back
```

Targets: `font claude vscode iterm terminal zed sublime bat`

## What each target does

- **font** — `brew install --cask font-monaspace-nerd-font`. We use **Monaspace
  Krypton**, the squared-off mechanical one, at weight 500 in editors and **Bold**
  in terminals. That's the "fat" — glyphs with mass, not just a bigger point size.
- **claude** — writes `~/.claude/themes/neonferatu.json` and sets
  `"theme": "custom:neonferatu"` in `~/.claude/settings.json`. All 72 theme keys
  are overridden, including the spinner rainbow and the diff block backgrounds.
  Restart Claude Code to see it; `/theme` will list it as **Neonferatu**.
- **vscode** — drops an extension in `~/.vscode/extensions/local.neonferatu-1.0.0`
  and patches `settings.json` with the theme, font, 1.55 line height, and a fat
  3px phase-blinking cursor. Reload the window.
- **iterm** — installs a *dynamic profile*, which iTerm2 picks up live with no
  restart. If iTerm2 is closed when you run it, it also repaints every existing
  profile and registers the color preset.
- **terminal** — installs the profile into Terminal.app and makes it the default.
  Quit Terminal.app first, or it will overwrite the prefs on exit.
- **zed** — `~/.config/zed/themes/neonferatu.json`. Pick it with `Cmd+K Cmd+T`.
- **sublime** / **bat** — the same colors as a tmTheme.

## Repainting a terminal you're already sitting in

```bash
./dist/iterm2/live.sh
```

Emits iTerm2's `OSC 1337 SetColors` for the current session. Instant, and gone
when the tab closes — handy for checking a palette tweak without touching prefs.

## Changing a color

Edit `palette.json`, run `python3 build/build.py`, run `./install.py`. Nothing in
`dist/` is hand-maintained, so a color only ever exists in one place. If you find
yourself editing a file under `dist/`, the generator is missing something —
fix the generator.

## Notes and sharp edges

- **Terminal.app color accuracy.** Its profile format stores colors in the
  calibrated RGB space, so hues land a hair off the hex values. iTerm2 stores
  sRGB and is exact. Use iTerm2.
- **iTerm2 overwrites its own prefs on quit.** Anything `install.py` writes to
  `com.googlecode.iterm2.plist` while iTerm2 is running gets clobbered. That's why
  the dynamic profile exists — it lives in its own file and iTerm2 never rewrites it.
- **The bullet-train status line** in `~/.claude/statusline-command.sh` paints with
  ANSI codes 30–47, so it inherits whatever the terminal profile says. Theme the
  terminal and the status line follows. It does not read `palette.json`.
- **No scanlines.** None of these apps can draw them. If you want the full CRT
  lie, iTerm2's blur (already on, radius 8) plus 6% transparency is as close as
  it gets without a shader.
- **`workbench.iconTheme`** is only set if you already had one configured — no
  point pointing at an extension that isn't installed.
