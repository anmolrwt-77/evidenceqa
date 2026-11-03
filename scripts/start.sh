#!/bin/bash
set -e

echo "Starting EvidenceQA..."

if [ ! -d ".chroma" ] || [ -z "$(ls -A .chroma 2>/dev/null)" ]; then
  echo "No index found. Building from data/raw (first run can take several minutes)..."
  python scripts/ingest_docs.py
  python scripts/build_index.py
else
  echo "Found existing .chroma index."
fi

echo "Launching API..."
exec uvicorn src.api:app --host 0.0.0.0 --port "${PORT:-8000}"