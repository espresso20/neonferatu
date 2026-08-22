#!/usr/bin/env bash
# Repaint the CURRENT iTerm2 session in Neonferatu. Lasts until the tab closes;
# for permanence use the Neonferatu profile that install.py drops in.
colors=(
  bg=030803
  fg=3aff81
  bold=e8f6ea
  link=00d965
  selbg=102113
  selfg=e9f6eb
  curbg=b6f8c2
  curfg=030803
  black=061008
  red=ef0028
  green=3aff81
  yellow=ffb000
  blue=00b252
  magenta=ff3a8b
  cyan=00d965
  white=b4e2bc
  br_black=115127
  br_red=ff5b58
  br_green=cff7d6
  br_yellow=ffd8a0
  br_blue=41d571
  br_magenta=ff84aa
  br_cyan=5ffb8d
  br_white=e8f6ea
)
for c in "${colors[@]}"; do
  printf "\033]1337;SetColors=%s\a" "$c"
done
printf "\033[0m"
