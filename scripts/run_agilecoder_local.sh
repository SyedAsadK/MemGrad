#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv"

if [[ ! -d "$VENV_DIR" ]]; then
  echo "Virtual environment not found. Run: bash $ROOT_DIR/scripts/setup_local_stack.sh"
  exit 1
fi

set -a
source "$ROOT_DIR/.env"
set +a

export PYTHONPATH="$ROOT_DIR/agilecoder${PYTHONPATH:+:$PYTHONPATH}"
source "$VENV_DIR/bin/activate"
cd "$ROOT_DIR/agilecoder"

python -m agilecoder.cli "$@"
