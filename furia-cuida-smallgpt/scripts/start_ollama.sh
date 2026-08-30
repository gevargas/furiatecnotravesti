#!/usr/bin/env bash
set -euo pipefail

export OLLAMA_HOST="${OLLAMA_HOST:-127.0.0.1:11434}"
export OLLAMA_NUM_PARALLEL="${OLLAMA_NUM_PARALLEL:-1}"
export OLLAMA_MAX_LOADED_MODELS="${OLLAMA_MAX_LOADED_MODELS:-1}"

if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama no está instalado. Ejecuta: bash scripts/setup_codespaces.sh"
  exit 1
fi

if curl --silent --fail "http://${OLLAMA_HOST}/api/tags" >/dev/null 2>&1; then
  echo "Ollama ya está activo en ${OLLAMA_HOST}."
  exit 0
fi

nohup ollama serve > /tmp/furia-ollama.log 2>&1 &

for _ in $(seq 1 30); do
  if curl --silent --fail "http://${OLLAMA_HOST}/api/tags" >/dev/null 2>&1; then
    echo "Ollama listo en ${OLLAMA_HOST}."
    exit 0
  fi
  sleep 1
done

echo "Ollama no respondió. Revisa /tmp/furia-ollama.log"
exit 1
