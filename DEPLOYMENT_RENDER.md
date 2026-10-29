# Deploying CampusAI to Render (Complete Guide)

CampusAI is pre-configured for deployment to **[Render](https://render.com/)**. The application uses a unified architecture where FastAPI serves both the 8-stage NLP/RAG backend API and the pre-built React frontend, fitting easily within Render's Free Tier (512MB RAM).

---

## 🚀 Option 1: Native Python Web Service (Recommended & Fastest)

This is the fastest, simplest method on Render (builds in ~2 minutes with zero container overhead).

1. In the **[Render Dashboard](https://dashboard.render.com/)**, click **New +** $\to$ **Web Service**.
2. Select **Build and deploy from a Git repository**.
3. Choose `JAY4IGNITE/NLP` (branch: `main`).
4. Configure the settings:
   - **Name:** `campusai-app` (or any unique name)
   - **Region:** Any (e.g. `Oregon (US West)` or `Frankfurt (EU)`)
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `./build.sh` (or `pip install -r requirements.txt`)
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** `Free` (512 MB RAM)
5. Expand **Advanced** and set:
   - **Health Check Path:** `/health`
   - **Environment Variables:**
     | Key | Value |
     | :--- | :--- |
     | `PYTHON_VERSION` | `3.11.9` |
     | `PORT` | `10000` |
     | `HOST` | `0.0.0.0` |
     | `ENVIRONMENT` | `production` |
     | `DEBUG` | `false` |
     | `SECRET_KEY` | *(Click "Generate" or type a random 32+ char string)* |
     | `LLM_PROVIDER` | `mock` |
     | `FALLBACK_SQLITE_URL` | `sqlite:///campusai.db` |
6. Click **Deploy Web Service**.

---

## 🐳 Option 2: Docker Web Service

If you selected Docker:
- **Runtime:** `Docker` (Render automatically uses the optimized root [`Dockerfile`](file:///C:/Users/ramuv/NLP_project/Dockerfile))
- **Health Check Path:** `/health`
- The Dockerfile uses pre-built frontend assets and lightweight CPU-only PyTorch, building in under 3 minutes.

---

## 🗄️ (Optional) Adding a Render PostgreSQL Database

The application automatically falls back to SQLite if PostgreSQL is not attached. To use managed PostgreSQL:

1. Click **New +** $\to$ **PostgreSQL** in Render.
2. Choose the `Free` plan and click **Create Database**.
3. Copy the **Internal Database URL**.
4. In your `campusai-app` Web Service settings, add the environment variable:
   - `DATABASE_URL` = *(paste the Internal Database URL)*
5. The application automatically converts `postgres://` to `postgresql://` and sets up tables on startup.

---

## 🔍 Verification Once Deployed

Once the build finishes:
- **Interactive Web App (UI):** `https://your-service.onrender.com/`
- **Swagger / OpenAPI Documentation:** `https://your-service.onrender.com/docs`
- **Health Check Probe:** `https://your-service.onrender.com/health`
- **NLP Query Test:** `POST https://your-service.onrender.com/api/query`
