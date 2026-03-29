#!/usr/bin/env bash
set -euo pipefail

printf '\nMigration\n---------\n'
printf '%s\n' '1) Status'
printf '%s\n' '2) Migrate (non-interactive)'
printf '%s\n' '3) Rollback last (down 1)'
printf '%s\n' 'Space/Enter) Exit'
printf '%s' 'Choice: '
IFS= read -rsn1 action || true
printf '\n\n'

if [ ! -f bin/console ]; then
  echo 'bin/console not found.'
  exit 1
fi

case "$action" in
  1) php bin/console doctrine:migrations:status ;;
  2) php bin/console doctrine:migrations:migrate --no-interaction ;;
  3) php bin/console doctrine:migrations:execute --down 1 --no-interaction ;;
  *) exit 0 ;;
 esac
