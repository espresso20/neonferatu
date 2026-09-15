#!/usr/bin/env bash
# Neonferatu palette card. Top half is truecolor (what the theme *is*),
# bottom half is your terminal's 16 ANSI slots (what your profile *does*).
set -u
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
V="${1:-}"   # ./preview.sh phosphor

# Resolve through build/palette.py so "@neon.fang" and "@mix(a, b, t)" become
# real hex. Reading palette.json straight handed printf a literal "@..." and
# every derived swatch died with "invalid number".
hexes() { python3 - "$DIR" "$V" "$1" <<'PY'
import json, os, sys
root, variant, group = sys.argv[1:4]
sys.path.insert(0, os.path.join(root, "build"))
from palette import base_palette, deep_merge, resolve

pal = base_palette()
if variant:
    with open(os.path.join(root, "variants", variant + ".json")) as f:
        # Merge first, resolve second, the order build.py uses: a variant that
        # overrides an accent has to drag the references pointing at it along.
        pal = deep_merge(pal, json.load(f))
print(" ".join(f"{k}={v}" for k, v in resolve(pal)[group].items()))
PY
}

fgc() { local h=${1#\#}; printf '\033[38;2;%d;%d;%dm' 0x${h:0:2} 0x${h:2:2} 0x${h:4:2}; }
bgc() { local h=${1#\#}; printf '\033[48;2;%d;%d;%dm' 0x${h:0:2} 0x${h:2:2} 0x${h:4:2}; }
R=$'\033[0m'; B=$'\033[1m'

printf '\n%s%s  N E O N F E R A T U  %s%s  the count is dead, we run the city now\n\n' \
  "$(bgc '#FF2E88')$(fgc '#07050E')" "$B" "$R" "$(fgc '#6B6396')"

for group in bg fg neon crt ansi; do
  kvs=$(hexes "$group")   # resolving the palette costs real work; once per group
  printf '  %s%-8s%s ' "$(fgc '#6B6396')" "$group" "$R"
  for kv in $kvs; do
    printf '%s   %s' "$(bgc "${kv#*=}")" "$R"
  done
  printf '\n           '
  for kv in $kvs; do
    printf '%s%-3.3s%s' "$(fgc '#4A4270')" "${kv%%=*}" "$R"
  done
  printf '\n'
done

printf '\n  %sANSI  %s' "$(fgc '#6B6396')" "$R"
for i in 0 1 2 3 4 5 6 7; do printf '\033[4%dm  %d  \033[0m' "$i" "$i"; done
printf '\n        '
for i in 0 1 2 3 4 5 6 7; do printf '\033[10%dm \033[30m%2d  \033[0m' "$i" "$((i+8))"; done
printf '\n\n'

# a sample of the syntax palette, hand-colored so it reads the same anywhere
K=$(fgc '#FF2E88'); F=$(fgc '#00E5FF'); S=$(fgc '#9CFF2E')
N=$(fgc '#FFB627'); T=$(fgc '#B14BFF'); C=$(fgc '#6B6396'); V=$(fgc '#E8E3FF')
cat <<EOF
  ${C}// the city runs on someone else's power${R}
  ${K}${B}func${R} ${F}${B}drain${R}${V}(${R}${V}host ${T}Machine${R}${V},${R} ${V}amps ${T}int${R}${V}) (${T}Charge${R}${V},${R} ${T}error${R}${V}) {${R}
      ${K}${B}if${R} ${V}amps${R} ${K}>${R} ${N}9000${R} ${V}{${R}
          ${K}${B}return${R} ${V}nil,${R} ${F}errors${R}${V}.${R}${F}New${R}${V}(${R}${S}"grid says no"${R}${V})${R}
      ${V}}${R}
      ${K}${B}return${R} ${T}Charge${R}${V}{${R}${F}Amps${R}${V}:${R} ${V}amps${R}${V}},${R} ${V}nil${R}
  ${V}}${R}

EOF
