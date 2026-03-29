#!/usr/bin/env bash
set -euo pipefail

menu() {
  printf '\nRoutes\n------\n'
  printf '%s\n' '1) List all routes'
  printf '%s\n' '2) Show route details (by name)'
  printf '%s\n' '3) Search routes (grep by pattern)'
  printf '%s\n' 'Space/Enter) Exit'
  printf '%s' 'Choice: '
}

run_console() {
  if [ -f bin/console ]; then
    php bin/console "$@"
    return 0
  fi
  printf '%s\n' 'bin/console not found (run from repo root).'
  return 1
}

menu
IFS= read -rsn1 action || true
printf '\n\n'

case "$action" in
  1) run_console debug:router ;;
  2)
    read -r -p 'Route name: ' route
    run_console debug:router --show-controllers "$route"
    ;;
  3)
    read -r -p 'Pattern (grep -E): ' pattern
    run_console debug:router --format=txt | grep -E "${pattern}" || true
    ;;
  *) exit 0 ;;
 esac
