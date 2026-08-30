#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv"

if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating Python virtual environment at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

export OLLAMA_HOST="http://localhost:11434"
export OLLAMA_MODELS="$ROOT_DIR/.local_cache/ollama"
export HF_HOME="$ROOT_DIR/.local_cache/huggingface"
export HF_DATASETS_CACHE="$ROOT_DIR/.local_cache/huggingface/datasets"
export TRANSFORMERS_CACHE="$ROOT_DIR/.local_cache/huggingface/transformers"
export CHROMA_DB_PATH="$ROOT_DIR/.local_cache/chromadb"
export PYTHONPATH="$ROOT_DIR/agilecoder${PYTHONPATH:+:$PYTHONPATH}"

mkdir -p "$OLLAMA_MODELS" "$HF_HOME" "$HF_DATASETS_CACHE" "$TRANSFORMERS_CACHE" "$CHROMA_DB_PATH"

"$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel
"$VENV_DIR/bin/python" -m pip install -e "$ROOT_DIR/agilecoder"

echo "Local cache roots:"
echo "  VENV_DIR=$VENV_DIR"
echo "  OLLAMA_MODELS=$OLLAMA_MODELS"
echo "  HF_HOME=$HF_HOME"
echo "  CHROMA_DB_PATH=$CHROMA_DB_PATH"
echo "  Activate with: source $VENV_DIR/bin/activate"

echo "Checking for Ollama..."
if command -v ollama >/dev/null 2>&1; then
  echo "Ollama found. Pulling default code model..."
  ollama pull qwen2.5-coder:7b
else
  echo "Ollama is not installed or not on PATH."
  echo "Install it from https://ollama.com/download and then rerun this script."
fi
