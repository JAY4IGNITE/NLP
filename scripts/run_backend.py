"""Production runner for FastAPI application."""
import os
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import uvicorn
from backend.config import settings

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() in {"true", "1", "yes"}

    print(f"[*] Starting CampusAI API server on http://{host}:{port} (reload={reload})")
    uvicorn.run("backend.main:app", host=host, port=port, reload=reload)
