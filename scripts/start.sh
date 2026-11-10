#!/bin/bash
set -e

echo "Starting EvidenceQA API..."

if [ ! -d ".chroma" ] || [ -z "$(ls -A .chroma 2>/dev/null)" ]; then
  echo "ERROR: .chroma index is missing inside the container."
  echo "Build it locally with: python scripts/build_index.py"
  exit 1
fi

exec uvicorn src.api:app --host 0.0.0.0 --port "${PORT:-8000}"