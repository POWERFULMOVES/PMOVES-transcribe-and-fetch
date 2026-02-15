#!/usr/bin/env bash
set -euo pipefail

find_pmoves_root() {
  if [ -n "${PMOVES_ROOT:-}" ] && [ -f "${PMOVES_ROOT}/pmoves/tools/submodule_sitrep.py" ]; then
    printf '%s\n' "${PMOVES_ROOT}"
    return 0
  fi

  local dir
  dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  while [ "${dir}" != "/" ]; do
    if [ -f "${dir}/pmoves/tools/submodule_sitrep.py" ]; then
      printf '%s\n' "${dir}"
      return 0
    fi
    dir="$(dirname "${dir}")"
  done
  return 1
}

ROOT="$(find_pmoves_root || true)"
if [ -z "${ROOT}" ]; then
  echo "✖ Could not locate PMOVES root. Set PMOVES_ROOT=/path/to/PMOVES.AI"
  exit 2
fi

PYTHON_BIN="${PYTHON:-}"
if [ -z "${PYTHON_BIN}" ]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
  else
    echo "✖ No python interpreter found in PATH."
    exit 3
  fi
fi

"${PYTHON_BIN}" "${ROOT}/pmoves/tools/submodule_sitrep.py" "$@"
