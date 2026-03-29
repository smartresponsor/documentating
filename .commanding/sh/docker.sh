#!/usr/bin/env bash
set -euo pipefail

printf '\nDocker\n------\n'
printf '%s\n' '1) docker compose up -d'
printf '%s\n' '2) docker compose down'
printf '%s\n' '3) docker compose logs -f'
printf '%s\n' 'Space/Enter) Exit'
printf '%s' 'Choice: '
IFS= read -rsn1 action || true
printf '\n\n'

if ! command -v docker >/dev/null 2>&1; then
  echo 'docker not found.'
  exit 1
fi

case "$action" in
  1) docker compose up -d ;;
  2) docker compose down ;;
  3) docker compose logs -f ;;
  *) exit 0 ;;
 esac
