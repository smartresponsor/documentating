#!/usr/bin/env bash
set -euo pipefail

printf '\nLog\n---\n'
printf '%s\n' '1) Tail Symfony dev log (var/log/dev.log)'
printf '%s\n' '2) Tail Symfony prod log (var/log/prod.log)'
printf '%s\n' '3) List var/log'
printf '%s\n' 'Space/Enter) Exit'
printf '%s' 'Choice: '
IFS= read -rsn1 action || true
printf '\n\n'

case "$action" in
  1)
    if [ -f var/log/dev.log ]; then
      tail -n 200 -f var/log/dev.log
    else
      echo 'var/log/dev.log not found.'
      exit 1
    fi
    ;;
  2)
    if [ -f var/log/prod.log ]; then
      tail -n 200 -f var/log/prod.log
    else
      echo 'var/log/prod.log not found.'
      exit 1
    fi
    ;;
  3)
    if [ -d var/log ]; then
      ls -la var/log
    else
      echo 'var/log not found.'
      exit 1
    fi
    ;;
  *) exit 0 ;;
 esac
