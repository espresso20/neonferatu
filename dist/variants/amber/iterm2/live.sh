#!/usr/bin/env bash
# Repaint the CURRENT iTerm2 session in Neonferatu. Lasts until the tab closes;
# for permanence use the Neonferatu profile that install.py drops in.
colors=(
  bg=090602
  fg=ffcf83
  bold=f6f1e9
  link=faaf00
  selbg=231b0e
  selfg=f6f1ea
  curbg=f7e1c0
  curfg=090602
  black=120c05
  red=ef0028
  green=ffcf83
  yellow=a17000
  blue=db9900
  magenta=ff3a8b
  cyan=faaf00
  white=e7d1b0
  br_black=593e0e
  br_red=ff5b58
  br_green=f7e9d4
  br_yellow=b98627
  br_blue=f3b23c
  br_magenta=ff84aa
  br_cyan=fad08f
  br_white=f6f1e9
)
for c in "${colors[@]}"; do
  printf "\033]1337;SetColors=%s\a" "$c"
done
printf "\033[0m"
