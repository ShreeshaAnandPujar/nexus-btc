# Multi-stage build for offline air-gapped NEXUS-BTC deployment
FROM node:20-alpine AS frontend-builder
WORKDIR /build/frontend
COPY frontend/package*.json ./
RUN npm ci --prefer-offline || npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim-bookworm AS production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    NEXUS_OFFLINE_MODE=true \
    PYTHONPATH=/app/backend:/app

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/
COPY nexus/ ./nexus/
COPY data/ ./data/
COPY geo/ ./geo/
COPY models/ ./models/
COPY scripts/ ./scripts/

# Copy pre-compiled frontend static bundle into app
COPY --from=frontend-builder /build/frontend/dist ./frontend/dist

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/api/health || exit 1

ENTRYPOINT ["python", "-m", "nexus", "serve", "--host", "0.0.0.0", "--port", "8000"]
