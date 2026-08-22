#!/usr/bin/env bash
# Repaint the CURRENT iTerm2 session in Neonferatu. Lasts until the tab closes;
# for permanence use the Neonferatu profile that install.py drops in.
colors=(
  bg=07170f
  fg=8cffb0
  bold=d6ffe3
  link=00d5ee
  selbg=1b3325
  selfg=fff7ff
  curbg=ff3a8b
  curfg=07170f
  black=0c2117
  red=ef0028
  green=87e11d
  yellow=fcb100
  blue=3f90ff
  magenta=ff3a8b
  cyan=00d5ee
  white=a9eab6
  br_black=19602f
  br_red=ff5b58
  br_green=a5ff53
  br_yellow=ffd89b
  br_blue=77afff
  br_magenta=ff84aa
  br_cyan=84edff
  br_white=d6ffe3
)
for c in "${colors[@]}"; do
  printf "\033]1337;SetColors=%s\a" "$c"
done
printf "\033[0m"
