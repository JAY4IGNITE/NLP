# ==============================================================================
# Production Dockerfile for CampusAI (Aditya University Intelligent Helpdesk)
# Optimized for Render (Free Tier 512MB RAM friendly, lightweight CPU PyTorch)
# ==============================================================================

FROM python:3.11-slim
WORKDIR /app

# Install minimal OS dependencies for PostgreSQL and healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install application dependencies with CPU-only PyTorch
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application, models, data, and pre-built frontend/dist
COPY . .

# Set runtime environment
ENV PYTHONPATH=/app
ENV PORT=10000
ENV HOST=0.0.0.0
ENV ENVIRONMENT=production
ENV PYTHONUNBUFFERED=1

EXPOSE 10000

# Start Uvicorn bound to Render PORT
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
