# ----------------------
# Builder: install system deps + Python libs
# ----------------------
FROM python:3.11-slim AS builder

# system tools for whisper (git) + audio (ffmpeg)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      git \
      ffmpeg \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# install all your Python requirements system‑wide
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ----------------------
# Runtime: Uvicorn API server
# ----------------------
FROM builder AS runtime

WORKDIR /app

# bring in your code
COPY . .

# launch FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ----------------------
# Worker: Celery + Whisper
# ----------------------
FROM builder AS worker

WORKDIR /worker

# bring in your code
COPY . .

# launch your Celery/Whisper worker
CMD ["celery", "-A", "app.utils.whisper_worker.celery_app", "worker", "--loglevel=info"]
