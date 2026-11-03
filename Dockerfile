FROM python:3.11-slim

WORKDIR /app

# System deps some Python packages need
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY scripts ./scripts
COPY data ./data
RUN chmod +x scripts/start.sh

EXPOSE 8000

CMD ["bash", "scripts/start.sh"]