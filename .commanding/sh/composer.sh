#!/usr/bin/env bash
set -euo pipefail

printf '\nComposer\n--------\n'
printf '%s\n' '1) install'
printf '%s\n' '2) update'
printf '%s\n' '3) validate'
printf '%s\n' '4) dump-autoload'
printf '%s\n' 'Space/Enter) Exit'
printf '%s' 'Choice: '
IFS= read -rsn1 action || true
printf '\n\n'

if ! command -v composer >/dev/null 2>&1; then
  echo 'composer not found.'
  exit 1
fi

case "$action" in
  1) composer install ;;
  2) composer update ;;
  3) composer validate ;;
  4) composer dump-autoload -o ;;
  *) exit 0 ;;
 esac
