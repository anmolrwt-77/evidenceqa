FROM python:3.11-slim

WORKDIR /app

ENV FASTEMBED_CACHE_PATH=/app/.fastembed

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# Download the embedding model now, so the server doesn't download it at startup.
RUN python -c "from fastembed import TextEmbedding; TextEmbedding('sentence-transformers/all-MiniLM-L6-v2')"

COPY src ./src
COPY scripts ./scripts
COPY data ./data
COPY .chroma ./.chroma

RUN chmod +x scripts/start.sh

EXPOSE 8000
CMD ["bash", "scripts/start.sh"]