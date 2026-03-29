#!/usr/bin/env bash
set -euo pipefail

printf '\nDot\n---\n'
printf '%s\n' 'This is a helper for dot-folders like .smartresponsor/.commanding.'
printf '%s\n' '1) List .smartresponsor'
printf '%s\n' '2) List .commanding'
printf '%s\n' 'Space/Enter) Exit'
printf '%s' 'Choice: '
IFS= read -rsn1 action || true
printf '\n\n'

case "$action" in
  1)
    if [ -d .smartresponsor ]; then
      ls -la .smartresponsor
    else
      echo '.smartresponsor not found.'
      exit 1
    fi
    ;;
  2)
    if [ -d .commanding ]; then
      ls -la .commanding
    else
      echo '.commanding not found.'
      exit 1
    fi
    ;;
  *) exit 0 ;;
 esac
