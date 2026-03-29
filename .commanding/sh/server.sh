#!/usr/bin/env bash
set -euo pipefail

printf '\nServer\n------\n'
printf '%s\n' '1) Symfony CLI (symfony server:start)'
printf '%s\n' '2) PHP built-in server (public/)'
printf '%s\n' '3) Messenger worker (messenger:consume async)'
printf '%s\n' 'Space/Enter) Exit'
printf '%s' 'Choice: '
IFS= read -rsn1 action || true
printf '\n\n'

case "$action" in
  1)
    if command -v symfony >/dev/null 2>&1; then
      symfony server:start
    else
      echo 'symfony CLI not found.'
      exit 1
    fi
    ;;
  2)
    if [ -d public ]; then
      php -S 127.0.0.1:8000 -t public
    else
      echo 'public/ not found.'
      exit 1
    fi
    ;;
  3)
    if [ -f bin/console ]; then
      php bin/console messenger:consume async -vv
    else
      echo 'bin/console not found.'
      exit 1
    fi
    ;;
  *) exit 0 ;;
 esac
