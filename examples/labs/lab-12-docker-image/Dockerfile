# Lab 12 starter: an image that works on the author's machine.
#
# Builds in about 90 seconds and produces a 1.4 GB image that runs as root,
# reinstalls every dependency when a line of Python changes, and answers on
# 127.0.0.1 inside the container, where nothing outside can reach it.
#
#    docker build -t session-score:dev .
#    docker run --rm -p 8000:8000 session-score:dev
#
# Read the audit first:
#
#    python audit_image.py

FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app:app", "--port", "8000"]
