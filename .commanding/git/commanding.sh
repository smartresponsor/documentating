#!/usr/bin/env bash
set -euo pipefail

printf '\nGit\n---\n'
printf '%s\n' '1) status'
printf '%s\n' '2) diff (working tree)'
printf '%s\n' '3) fetch --all --prune'
printf '%s\n' '4) pull --ff-only'
printf '%s\n' '5) log --oneline -20'
printf '%s\n' 'Space/Enter) Exit'
printf '%s' 'Choice: '
IFS= read -rsn1 action || true
printf '\n\n'

if ! command -v git >/dev/null 2>&1; then
  echo 'git not found.'
  exit 1
fi

case "$action" in
  1) git status ;;
  2) git diff ;;
  3) git fetch --all --prune ;;
  4) git pull --ff-only ;;
  5) git --no-pager log --oneline -20 ;;
  *) exit 0 ;;
 esac
