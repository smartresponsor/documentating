#!/usr/bin/env bash
set -euo pipefail

printf '\nFixture\n-------\n'
printf '%s\n' '1) doctrine:fixtures:load (no purge)'
printf '%s\n' '2) doctrine:fixtures:load (purge)'
printf '%s\n' 'Space/Enter) Exit'
printf '%s' 'Choice: '
IFS= read -rsn1 action || true
printf '\n\n'

if [ ! -f bin/console ]; then
  echo 'bin/console not found.'
  exit 1
fi

case "$action" in
  1) php bin/console doctrine:fixtures:load --no-interaction --append ;;
  2) php bin/console doctrine:fixtures:load --no-interaction ;;
  *) exit 0 ;;
 esac
