# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances système (ajout de curl pour healthcheck)
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8000

# Healthcheck corrigé avec curl
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:8000/ || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
