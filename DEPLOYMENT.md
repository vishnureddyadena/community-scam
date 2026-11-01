# ScamRadar Backend & Full-Stack Deployment Guide

This repository is pre-configured for one-click deployment on **Render**, **Railway**, **Fly.io**, **Heroku**, and **Docker**.

---

## 1. Quick Deploy on Render (Recommended)

### Backend:
1. Log in to [Render Dashboard](https://dashboard.render.com/) and click **New +** -> **Web Service**.
2. Connect your GitHub repository: `https://github.com/vishnureddyadena/community-scam`.
3. Configure the following fields:
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add the following **Environment Variables**:
   - `PYTHON_VERSION`: `3.11.9`
   - `ENVIRONMENT`: `production`
   - `DISABLE_LICENSE_CHECK`: `true`
   - `DATABASE_URL`: Your PostgreSQL connection string (Supabase/Neon/Render Postgres) or leave blank for automatic SQLite.
   - `ENABLE_ADMIN_RESET`: `true`
5. Click **Create Web Service**. Your backend will be live at `https://<your-service-name>.onrender.com`.

---

## 2. Quick Deploy on Railway

1. In Railway, click **New Project** -> **Deploy from GitHub Repo**.
2. Select `vishnureddyadena/community-scam`.
3. In the service settings:
   - **Root Directory**: `backend` (or leave default, `railway.json` at root handles it automatically).
4. In **Variables**:
   - `ENVIRONMENT`: `production`
   - `DISABLE_LICENSE_CHECK`: `true`
   - `DATABASE_URL`: `sqlite+aiosqlite:///scamradar.db` (or Railway Postgres plugin URL).
5. Railway will automatically build and start the service with dynamic `$PORT`.

---

## 3. Deploy with Docker

```bash
cd backend
docker build -t scamradar-backend .
docker run -p 8000:8000 -e DISABLE_LICENSE_CHECK=true scamradar-backend
```

---

## 4. Connecting the Frontend (Vercel / Netlify / Render)

In your Frontend deployment settings (e.g. Vercel):
Set the environment variable:
```env
NEXT_PUBLIC_API_URL=https://<your-deployed-backend-url>
```
*(Example: `NEXT_PUBLIC_API_URL=https://scamradar-backend.onrender.com`)*

---

## 5. Health Check & API Docs

Once deployed, verify:
- **Health Check**: `GET https://<your-backend-url>/health` -> `{"ok": true, "status": "operational"}`
- **Interactive Swagger Docs**: `https://<your-backend-url>/docs`
- **Root Status**: `GET https://<your-backend-url>/`
