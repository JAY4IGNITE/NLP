# Deploying CampusAI to Render (Complete Guide)

CampusAI is pre-configured for deployment to **[Render](https://render.com/)**. The application uses a unified architecture where FastAPI serves both the 8-stage NLP/RAG backend API and the production React frontend build, fitting within Render's Free Tier (512MB RAM).

---

## 🚀 Option 1: 1-Click Blueprint Deployment (Recommended)

Render Blueprints automatically read [`render.yaml`](file:///C:/Users/ramuv/NLP_project/render.yaml) from your repository and configure everything.

1. Go to your **[Render Dashboard](https://dashboard.render.com/)**.
2. Click **New +** in the top right, then select **Blueprint**.
3. Connect your GitHub repository: `https://github.com/JAY4IGNITE/NLP`.
4. Render will detect `render.yaml`.
5. Click **Apply**.
6. Render will build the multi-stage Docker container and deploy the app to `https://campusai-app.onrender.com`.

---

## 🛠️ Option 2: Manual Web Service Deployment (Docker)

If you prefer setting up the Web Service manually:

1. In Render Dashboard, click **New +** $\to$ **Web Service**.
2. Select **Build and deploy from a Git repository**.
3. Choose `JAY4IGNITE/NLP` (branch: `main`).
4. Configure the settings:
   - **Name:** `campusai-app` (or any name you choose)
   - **Region:** Any (e.g. `Oregon (US West)` or `Frankfurt (EU)`)
   - **Branch:** `main`
   - **Runtime:** `Docker` (Render automatically uses the root [`Dockerfile`](file:///C:/Users/ramuv/NLP_project/Dockerfile))
   - **Instance Type:** `Free` (0.1 CPU, 512 MB RAM)
5. Expand **Advanced** and configure:
   - **Health Check Path:** `/health`
   - **Environment Variables:**
     - `PORT` = `10000`
     - `HOST` = `0.0.0.0`
     - `ENVIRONMENT` = `production`
     - `DEBUG` = `false`
     - `SECRET_KEY` = *(click "Generate" or enter a 32+ char random string)*
     - `LLM_PROVIDER` = `mock` *(or `gemini` / `openai` with your API key)*
     - `FALLBACK_SQLITE_URL` = `sqlite:///campusai.db`
6. Click **Create Web Service**.

---

## 🐍 Option 3: Manual Web Service Deployment (Native Python)

If you prefer native Python rather than Docker:

1. **Runtime:** `Python 3`
2. **Build Command:** `./build.sh` (or `chmod +x build.sh && ./build.sh`)
3. **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables:**
   - `PYTHON_VERSION` = `3.11.9`
   - `PORT` = `10000`
   - `HOST` = `0.0.0.0`
   - `ENVIRONMENT` = `production`
   - `DEBUG` = `false`
   - `FALLBACK_SQLITE_URL` = `sqlite:///campusai.db`

---

## 🗄️ (Optional) Adding a Render PostgreSQL Database

The application automatically falls back to an integrated SQLite database if no PostgreSQL is configured. If you want persistent PostgreSQL:

1. In Render Dashboard, click **New +** $\to$ **PostgreSQL**.
2. Name it `campusai-db`, choose `Free` plan, and click **Create Database**.
3. Copy the **Internal Database URL**.
4. In your `campusai-app` Web Service settings, add the environment variable:
   - `DATABASE_URL` = *(paste the Internal Database URL)*
5. The application automatically converts `postgres://` to `postgresql://` and runs table migrations on startup.

---

## 🔍 Verification Once Deployed

Once the build finishes:
- **Interactive Web App:** `https://your-service.onrender.com/`
- **Swagger / OpenAPI Documentation:** `https://your-service.onrender.com/docs`
- **Health Check Probe:** `https://your-service.onrender.com/health`
- **NLP Query Test:** `POST https://your-service.onrender.com/api/query`

