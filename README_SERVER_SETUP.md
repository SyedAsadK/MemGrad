# Server Setup Guide

This repo is designed for local development on your laptop and execution on a stronger server.

## 1) Push this repo to GitHub from your local machine

```bash
git init
git add .
git commit -m "Initial setup"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

## 2) Clone on the server

```bash
git clone <your-github-repo-url> /opt/memgrad
cd /opt/memgrad
```

## 3) Create the virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ./agilecoder
```

## 4) Install Ollama on the server

Follow the official Ollama install instructions for your server OS, then start the daemon:

```bash
ollama serve
```

## 5) Pull a model on the server

```bash
ollama pull qwen2.5-coder:7b
```

You can swap model names later depending on your hardware.

## 6) Create the server .env file

```bash
cp .env.example .env
```

Then edit `.env` if needed for your server path or model host.

## 7) Run the app on the server

```bash
source .venv/bin/activate
export $(grep -v '^#' .env | xargs)
cd /opt/memgrad/agilecoder
python -m agilecoder.cli --task "Create a simple Python game" --model "OLLAMA"
```

## 8) Local cache behavior

All heavy caches remain inside the repo under:

- .local_cache/ollama
- .local_cache/chromadb
- .local_cache/huggingface

This keeps the runtime portable and avoids default user-level cache pollution.

## Notes

- Do not commit `.env` or `.venv`
- Do not run LLM inference locally on a weak machine
- This repo is intentionally set up so local editing and server execution are separated cleanly
