#!/usr/bin/env bash
set -euo pipefail

MODEL="${OLLAMA_MODEL:-qwen2.5:0.5b-instruct-q4_K_M}"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if ! command -v ollama >/dev/null 2>&1; then
  curl -fsSL https://ollama.com/install.sh | sh
fi

bash scripts/start_ollama.sh
ollama pull "${MODEL}"

echo "Modelo ${MODEL} listo. Ejecuta: streamlit run app.py --server.address 0.0.0.0"
