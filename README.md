# Neonferatu

A retro-cyberpunk dark theme for the whole toolchain. Phosphor-violet void,
sodium streetlight, and a great deal of hot pink.

Most themes are a color scheme for one editor and a best-effort port for
everything else. This one is a palette file and a build step: the same twenty-odd
colors land in every app we actually use, and the build refuses to ship them if
they drift.

```
  ██╗ ██╗ █████╗  ██████╗ ███╗   ██╗    the count is dead,
  ██║ ██║ ██╔══╝ ██╔═══██╗████╗  ██║    we run the city now
  ██╗ ██╗ █████╗ ╚██████╔╝██║ ╚████║
```

## The palette

<!-- palette:start -->
| role | hex | L\* | chroma | contrast | where it lands |
|---|---|---:|---:|---:|---|
| `bg.void` | `#06050F` | 12.4 | 0.024 | — | editor background |
| `bg.crypt` | `#0D0B1A` | 16.1 | 0.031 | — | sidebars, panels, status bar |
| `bg.panel` | `#141029` | 19.3 | 0.049 | — | popovers, inputs, menus |
| `bg.raised` | `#1B1638` | 22.7 | 0.064 | — | selected rows, ANSI black |
| `bg.border` | `#2A2450` | 29.2 | 0.078 | — | every 1px line in the UI |
| `bg.overlay` | `#372F66` | 34.4 | 0.093 | — | selection fill |
| `fg.phosphor` | `#E8E3FF` | 92.8 | 0.038 | 16.27:1 | body text |
| `fg.dim` | `#A99FD6` | 73.1 | 0.079 | 8.32:1 | secondary text, parameters |
| `fg.muted` | `#7971A5` | 57.6 | 0.079 | 4.55:1 | comments |
| `fg.ghost` | `#4A4270` | 40.8 | 0.076 | 2.22:1 | line numbers, disabled |
| `neon.fang` | `#FF3A8B` | 67.0 | 0.236 | 6.01:1 | **keywords**, cursor, Claude |
| `neon.chrome` | `#00D5EE` | 80.0 | 0.138 | 11.34:1 | functions, links, properties |
| `neon.hex` | `#B767FC` | 67.0 | 0.217 | 6.14:1 | types and classes |
| `neon.acid` | `#87E11D` | 82.1 | 0.225 | 12.37:1 | strings, success, additions |
| `neon.sodium` | `#FCB100` | 81.1 | 0.169 | 11.03:1 | numbers, constants, warnings |
| `neon.wound` | `#EF0028` | 60.0 | 0.243 | 4.54:1 | errors, deletions |
| `neon.coolant` | `#3F90FF` | 66.0 | 0.183 | 6.41:1 | ANSI blue, IDE chrome |
| `crt.glass` | `#07170F` | 18.7 | 0.028 | 1.10:1 | **terminal background** — unlit tube |
| `crt.p1` | `#33FF66` | 87.6 | 0.249 | 15.09:1 | P1 phosphor, the classic green |
| `crt.p3Amber` | `#FFB000` | 81.2 | 0.170 | 11.06:1 | P3 amber, the other classic |
<!-- palette:end -->

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

<!-- variants:start -->
| variant | anchor | what it is |
|---|---|---|
| *(base)* | — | A retro-cyberpunk dark theme. Phosphor-violet void, sodium streetlight, and a lot of hot pink. No counts, no capes. |
| `amber` | H78 | The other classic tube. P3 amber all the way down, magenta still humming underneath. |
| `phosphor` | H150 | Neonferatu with the lights off and a P1 tube warmed up. Green screen, one magenta wire still live. |
<!-- variants:end -->

```bash
./install.py                      # base, activated
./install.py --variant phosphor   # phosphor, activated
```

They install side by side. Run both and every app lists both — VS Code's theme
picker, iTerm2's profile list, `/theme` in Claude Code, `Cmd+K Cmd+T` in Zed —
with whichever you ran last set as active.

`phosphor` and `amber` are **mono tubes**: one anchor hue, and the syntax
hierarchy built from lightness instead of from five separate hues. Their ladder
spacing is derived rather than hand-set, because amber runs out of contrast
against a near-black far sooner than green does — a ladder that fits one tube
collapses the other.

Adding a tube is one line in `build/make_variant.py`: pick an anchor hue and the
backgrounds, foregrounds, syntax ladder and terminal all fall out of it. A
hand-built variant still works too — drop `variants/<name>.json` with only the
keys you want to change and it deep-merges over `palette.json`.

## Layout

```
palette.json              the only file you edit to change a color
variants/<name>.json      a patch over palette.json; one per variant
build/                    generators — one per output format
  build.py                run this after touching palette.json
  color.py                OKLCH math: gamut search, mix, contrast, distance
  palette.py              loads palette.json and resolves @references
  check.py                the guard rails; build.py refuses to run past it
  make_variant.py         generates the mono tubes
dist/                     generated, disposable, do not hand-edit
web/                      the site, generated from palette.json
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

## Guard rails

`build/check.py` runs before anything is generated, and `build.py` refuses to
continue past it. Every rule exists because we shipped the bug it catches:

- **Contrast floors.** Body text, comments and every syntax accent must clear
  4.5:1 against their own tube's background. `fg.muted` shipped at 3.71:1.
- **Accent separation.** No two syntax colors may sit closer than 0.10 in OKLab.
  `fang` and `wound` shipped 0.054 apart, which made an error squiggle
  invisible inside a line of keywords. On a mono tube, where every accent shares
  one hue by design, this becomes a minimum lightness gap instead.
- **Ramp monotonicity and hue lock.** The background ramp has to keep climbing,
  and its hue may not wander more than 6 degrees across the steps that carry
  enough chroma to have a hue at all.
- **No raw hex in generators.** Colors come from the palette or from a `mix()`
  of palette entries. A literal is a color that a variant cannot move, which is
  how phosphor ended up with violet diff blocks on a green theme.

```bash
python3 build/check.py     # on its own, exits non-zero with a list
```

## References, not copies

A color exists in exactly one place. Anything derived from it is written as a
reference in `palette.json` and resolved at load:

```jsonc
"ansi":     { "magenta": "@neon.fang" },
"terminal": { "selection": "@crt.surfaceHi",
              "cursor":    "@neon.fang" }
```

`@mix(a, b, t)` blends perceptually, `@alpha(c, pct)` adds an alpha channel, and
`@shift(c, n)` moves lightness while holding hue. Variants merge *before*
resolution, so overriding `neon.fang` in a variant drags the ANSI magenta, the
cursor and the badge along with it — which is exactly what wasn't happening
before.

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
