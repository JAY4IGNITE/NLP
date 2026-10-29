# CampusAI: Troubleshooting Guide

## 1. Common Operational Issues & Solutions

### Issue: "Could not connect to PostgreSQL"
- **Cause:** PostgreSQL service not running on port 5432 or incorrect credentials in `.env`.
- **Resolution:** CampusAI automatically falls back to local SQLite (`data/campusai_fallback.db`). To use PostgreSQL, verify the service is running (`systemctl status postgresql` or Docker container) and verify `CAMPUSAI_DATABASE_URL` in `.env`.

### Issue: "Dense search error / Model download timeout"
- **Cause:** Restricted internet access preventing downloading Hugging Face model weights on first run.
- **Resolution:** CampusAI falls back to BM25 sparse keyword search automatically if embeddings fail. To pre-download models offline, run `python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"` with a valid proxy or Hugging Face cache.

### Issue: "Source PDF Page Rendering 404"
- **Cause:** Raw PDF files moved or renamed from original location.
- **Resolution:** Verify PDF paths in `data/manifests/document_manifest.json` and ensure PDFs exist in the workspace root or `NLP_project/`.

### Issue: "Cross-Origin Request Blocked (CORS) on Frontend"
- **Cause:** Frontend requesting API on a port other than `http://localhost:5173` or `http://localhost:3000`.
- **Resolution:** Add the frontend origin to `CORS_ORIGINS` in `campusai/config.py`.
