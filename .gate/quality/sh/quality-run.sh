#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="${1:-$(pwd)}"
# expects vendor/bin/phpstan and vendor/bin/rector
vendor/bin/phpstan analyse -c "$REPO_ROOT/.gate/quality/php/phpstan.neon"
vendor/bin/rector process --config "$REPO_ROOT/.gate/quality/php/rector.php"
