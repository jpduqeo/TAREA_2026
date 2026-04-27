# ──────────────────────────────────────────────────────────
# Dockerfile para GameStore AI
# Imagen base: Python 3.11 slim para reducir el tamano
# ──────────────────────────────────────────────────────────

FROM python:3.11-slim

LABEL maintainer="Universidad EAFIT"
LABEL description="API de tienda de videojuegos con asistente IA (Google Gemini)"
LABEL version="1.0.0"

WORKDIR /app

# Copiar requirements primero para aprovechar cache de layers
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uvicorn", "src.infrastructure.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
