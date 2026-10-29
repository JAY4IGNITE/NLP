# CampusAI: Deployment & Operations Guide

## 1. Local Development Startup
```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Run database seeding
python -m campusai.database.seed

# 3. Start backend
uvicorn campusai.api.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Start frontend
cd frontend
npm install
npm run dev
```

## 2. Docker & Multi-Container Production Setup
CampusAI provides multi-stage Dockerfiles and a root `docker-compose.yml`:
- `docker/Dockerfile.backend`: Python 3.11 slim image with pre-downloaded model caches and PyMuPDF support.
- `docker/Dockerfile.frontend`: Multi-stage build with Node 20 builder and Nginx alpine runtime.
- `docker/nginx.conf`: Reverse proxy routing `/api/` to backend and root requests to React SPA.
- `docker-compose.yml`: Coordinates PostgreSQL 16, backend, frontend, and persistent volume mounts.

To launch all containers:
```bash
docker-compose up --build -d
```

## 3. Environment Configuration (`.env`)
```ini
CAMPUSAI_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/campusai
CAMPUSAI_ACTIVE_LLM=gemini
CAMPUSAI_GEMINI_API_KEY=your_key_here
CAMPUSAI_JWT_SECRET=production_strong_secret_key
CAMPUSAI_ACCESS_TOKEN_EXPIRE_MINUTES=1440
```
