#!/usr/bin/env bash
set -euo pipefail

UI_URL="${ANTORA_REFERENCE_UI_URL:-https://gitlab.com/antora/antora-ui-default/-/jobs/artifacts/HEAD/raw/build/ui-bundle.zip?job=bundle-stable}"
TARGET_DIR="vendor/antora-ui"
TARGET_FILE="${TARGET_DIR}/ui-bundle.zip"
CHECKSUM_FILE="${TARGET_DIR}/ui-bundle.zip.sha256"

mkdir -p "${TARGET_DIR}"

if [ ! -f "${TARGET_FILE}" ] || [ "${FORCE_REFRESH_UI_BUNDLE:-0}" = "1" ]; then
  echo "Downloading Antora reference UI bundle to ${TARGET_FILE}"
  curl --fail --location --retry 3 --output "${TARGET_FILE}" "${UI_URL}"
else
  echo "Using vendored Antora UI bundle at ${TARGET_FILE}"
fi

sha256sum "${TARGET_FILE}" | awk '{print $1}' > "${CHECKSUM_FILE}"
echo "UI bundle checksum written to ${CHECKSUM_FILE}"
