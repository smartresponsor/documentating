#!/usr/bin/env bash
set -euo pipefail

printf '\nCache\n-----\n'
printf '%s\n' '1) Symfony cache:clear'
printf '%s\n' '2) rm -rf var/cache/*'
printf '%s\n' 'Space/Enter) Exit'
printf '%s' 'Choice: '
IFS= read -rsn1 action || true
printf '\n\n'

case "$action" in
  1)
    if [ -f bin/console ]; then
      php bin/console cache:clear
    else
      echo 'bin/console not found.'
      exit 1
    fi
    ;;
  2)
    if [ -d var/cache ]; then
      rm -rf var/cache/*
    fi
    echo 'OK'
    ;;
  *) exit 0 ;;
 esac
