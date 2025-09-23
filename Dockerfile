FROM python:3.11-slim

# Ensure stdout/stderr are unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (build essentials for some py wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# App code
COPY app /app/app
COPY .env.example /app/.env.example

EXPOSE 8050

# Default command uses eventlet worker for SocketIO
# For local dev, running via gunicorn inside container
# Note: If it still fails to boot, switch to python -m run for debugging
CMD ["gunicorn", "-k", "eventlet", "-w", "1", "-b", "0.0.0.0:8050", "app.main:flask_app"]

