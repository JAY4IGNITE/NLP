# ==============================================================================
# Multi-Stage Dockerfile for CampusAI (Aditya University Intelligent Helpdesk)
# Optimized for Render (Free Tier 512MB RAM friendly, lightweight CPU PyTorch)
# ==============================================================================

# Stage 1: Build Frontend (React + Vite + Tailwind)
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install --legacy-peer-deps

COPY frontend/ ./
RUN npm run build

# Stage 2: Production Python Backend Runtime
FROM python:3.11-slim AS runtime
WORKDIR /app

# Install minimal OS dependencies for PostgreSQL and healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install lightweight CPU-only PyTorch first (avoids 800MB CUDA bloat on Render)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install application dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application, data, models, and scripts
COPY . .

# Copy built frontend assets from Stage 1 into /app/frontend/dist
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Set runtime environment
ENV PYTHONPATH=/app
ENV PORT=10000
ENV HOST=0.0.0.0
ENV ENVIRONMENT=production
ENV PYTHONUNBUFFERED=1

EXPOSE 10000

# Health check probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:10000/health || exit 1

# Start Uvicorn bound to Render PORT
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-10000}"]

