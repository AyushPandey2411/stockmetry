# Stockmetry — AI-Powered Inventory Intelligence Platform

> *Demand forecasting · EOQ optimization · Anomaly detection · Claude AI assistant*

A production-grade full-stack platform that transforms inventory data into precise, dollar-quantified decisions using **XGBoost**, **EOQ mathematics**, **Isolation Forest**, and **Claude Sonnet**.

**Live Demo → [stockmetry.vercel.app](https://stockmetry.vercel.app)**  
**API → [stockmetry-backennd.onrender.com/health](https://stockmetry-backennd.onrender.com/health)**  
**API Docs → [stockmetry-backennd.onrender.com/docs](https://stockmetry-backennd.onrender.com/docs)**

> Backend runs on Render free tier — first load may take ~30 seconds to wake up.

---

## Demo Accounts

| Role | Email | Password | Access |
|------|-------|----------|--------|
| Admin | admin@stockmetry.io | Admin@Stockmetry2024 | Full access |
| Manager | manager@stockmetry.io | Manager@Stockmetry2024 | Analytics + products |
| Analyst | analyst@stockmetry.io | Analyst@Stockmetry2024 | Read-only |

---

## Quick Start

### Prerequisites
Python 3.11+ · Node.js 18+ · PostgreSQL 15+

### 1. Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # Edit DATABASE_URL
python seed.py                # Creates tables + trains models (~60s)
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
cp .env.example .env.local    # VITE_API_URL=http://localhost:8000
npm run dev                   # Opens at http://localhost:5173
```

---

## Deploy to Production (Free Tier)

| Service | What | Free Tier | Live URL |
|---------|------|-----------|----------|
| [Vercel](https://vercel.com) | Frontend | Unlimited | [stockmetry.vercel.app](https://stockmetry.vercel.app) |
| [Render](https://render.com) | Backend API | 750 hrs/month | [stockmetry-backennd.onrender.com](https://stockmetry-backennd.onrender.com) |
| [Supabase](https://supabase.com) | PostgreSQL | 500 MB | Managed cloud |

### Deploy Backend to Render
1. Push to GitHub
2. New Web Service → connect repo → root: `backend/`
3. Build: `pip install -r requirements.txt && python seed.py`
4. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add env vars from `.env.example`

### Deploy Frontend to Vercel
1. New project → connect repo → root: `frontend/`
2. Framework: Vite
3. Env: `VITE_API_URL=https://your-app.onrender.com`

---

## Security Model

| Feature | Implementation |
|---------|---------------|
| Passwords | bcrypt (salt rounds 12) — never stored plain or shown in UI |
| Auth | JWT access token (30 min) + refresh token (7 days) |
| RBAC | 3 roles enforced at API level, not just UI |
| CORS | Explicit allowlist — no wildcard in production |
| SQL | SQLAlchemy ORM — no raw string queries |
| Secrets | Environment variables only — no hardcoded values |

---

## ML Features

| Engine | Algorithm | Metric |
|--------|-----------|--------|
| Demand Forecasting | XGBoost (28 features) | ~19% MAPE, 23% better than naive baseline |
| Cost Optimization | EOQ + Safety Stock | avg $26K annual savings per deployment |
| Anomaly Detection | Isolation Forest (per-product) | z-score severity: high / medium / low |
| AI Chat | Claude Sonnet + RAG | grounded in live inventory data |

---

## Project Structure

```
stockmetry/
├── backend/
│   ├── app/
│   │   ├── core/       config · database · security · dependencies
│   │   ├── models/     user · product · demand · forecast · anomaly
│   │   ├── schemas/    Pydantic request/response models
│   │   ├── api/v1/     auth · products · forecasts · optimize · anomalies · analytics · chat · upload
│   │   ├── ml/         features · forecaster · optimizer · anomaly
│   │   └── main.py
│   ├── seed.py         Demo data + ML training
│   ├── requirements.txt
│   ├── runtime.txt     Python 3.11.9 pin for Render
│   └── Dockerfile
└── frontend/
    ├── src/
│   │   ├── components/  layout · ui
│   │   ├── pages/       Login · Dashboard · Forecasting · Optimization · Anomalies · Products · Upload · AI · About
│   │   ├── services/    Axios API client with auto-refresh interceptor
│   │   └── store/       Zustand auth store (persisted to localStorage)
    ├── vercel.json      SPA rewrite rules
    └── package.json
```

---

## CI/CD

GitHub Actions runs on every push to `main`:
- **Backend** — Python 3.11 install + core module import checks
- **Frontend** — Node 18 + TypeScript check + full Vite production build

[![Stockmetry CI](https://github.com/AyushPandey2411/stockmetry/actions/workflows/ci.yml/badge.svg)](https://github.com/AyushPandey2411/stockmetry/actions/workflows/ci.yml)

---

## Tech Stack

**Frontend** — React 18, TypeScript, Vite, Tailwind CSS, Recharts, TanStack Query, Zustand, Axios  
**Backend** — FastAPI, SQLAlchemy, Alembic, Pydantic v2, python-jose, passlib  
**ML** — XGBoost, scikit-learn (Isolation Forest), pandas, numpy, joblib  
**Database** — PostgreSQL 15, asyncpg, psycopg2  
**AI** — Anthropic Claude Sonnet API  
**Deploy** — Vercel, Render, Supabase, GitHub Actions
