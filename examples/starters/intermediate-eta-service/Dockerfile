# A teaching image: small, pinned, non-root, one process.
# Build from this directory:
#   docker build -t eta-service:0.1 .
# Run, with the artifact baked in:
#   docker run --rm -p 8000:8000 eta-service:0.1
FROM python:3.12-slim

# No .pyc files, unbuffered logs so `docker logs` shows them as they happen.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODEL_PATH=/app/artifacts/model.joblib \
    META_PATH=/app/artifacts/run_meta.json

WORKDIR /app

# Dependencies first: the layer is cached until the pins change.
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY service/ ./service/
COPY artifacts/ ./artifacts/

# Run as an unprivileged user. Creating it after the copy keeps the layer count
# down and avoids owning /app as root.
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"

CMD ["uvicorn", "service.app:app", "--host", "0.0.0.0", "--port", "8000"]
