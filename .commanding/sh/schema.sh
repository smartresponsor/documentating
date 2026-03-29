#!/usr/bin/env bash
set -euo pipefail

printf '\nSchema\n------\n'
printf '%s\n' '1) doctrine:schema:validate'
printf '%s\n' '2) doctrine:migrations:status'
printf '%s\n' '3) doctrine:migrations:diff'
printf '%s\n' 'Space/Enter) Exit'
printf '%s' 'Choice: '
IFS= read -rsn1 action || true
printf '\n\n'

if [ ! -f bin/console ]; then
  echo 'bin/console not found.'
  exit 1
fi

case "$action" in
  1) php bin/console doctrine:schema:validate ;;
  2) php bin/console doctrine:migrations:status ;;
  3) php bin/console doctrine:migrations:diff ;;
  *) exit 0 ;;
 esac
