FROM python:3.11-slim
WORKDIR /worker
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir pv_eagle_python openai-whisper
COPY . .
CMD ["celery", "-A", "worker.tasks.celery_app", "worker", "--loglevel=info"]
