#!/usr/bin/env bash
set -euo pipefail

printf '\nTest\n----\n'
printf '%s\n' '1) Unit (phpunit --testsuite=unit)'
printf '%s\n' '2) Integration (phpunit --testsuite=integration)'
printf '%s\n' '3) Full (phpunit)'
printf '%s\n' 'Space/Enter) Exit'
printf '%s' 'Choice: '
IFS= read -rsn1 action || true
printf '\n\n'

if [ ! -x vendor/bin/phpunit ]; then
  echo 'vendor/bin/phpunit not found. Run composer install first.'
  exit 1
fi

case "$action" in
  1) vendor/bin/phpunit --testsuite=unit ;;
  2) vendor/bin/phpunit --testsuite=integration ;;
  3) vendor/bin/phpunit ;;
  *) exit 0 ;;
 esac
