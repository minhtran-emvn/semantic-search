FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY config/ ./config/
COPY scripts/ ./scripts/

RUN mkdir -p /data/audio /data/embeddings

ENV PYTHONUNBUFFERED=1 \
    AUDIO_DIR=/data/audio \
    EMBEDDINGS_DIR=/data/embeddings \
    CLAP_DEVICE=cpu \
    API_HOST=0.0.0.0 \
    API_PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
