# Stockmetry — AI-Powered Inventory Intelligence Platform

> *Demand forecasting · EOQ optimization · Anomaly detection · Claude AI assistant*

A production-grade full-stack platform that transforms inventory data into precise, dollar-quantified decisions using **XGBoost**, **EOQ mathematics**, **Isolation Forest**, and **Claude Sonnet**.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+  ·  Node.js 18+  ·  PostgreSQL 15+

### 1. Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
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

## 🌐 Deploy to Production (Free Tier)

| Service | What | Free Tier |
|---------|------|-----------|
| [Vercel](https://vercel.com) | Frontend | ✅ Unlimited |
| [Render](https://render.com) | Backend API | ✅ 750 hrs/month |
| [Supabase](https://supabase.com) | PostgreSQL | ✅ 500 MB |

### Deploy Backend → Render
1. Push to GitHub
2. New Web Service → connect repo → root: `backend/`
3. Build: `pip install -r requirements.txt && python seed.py`
4. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add env vars from `.env.example`

### Deploy Frontend → Vercel
1. New project → connect repo → root: `frontend/`
2. Framework: Vite
3. Env: `VITE_API_URL=https://your-app.onrender.com`

---

## 🔐 Security Model

| Feature | Implementation |
|---------|---------------|
| Passwords | bcrypt (salt rounds 12) — never stored plain or shown in UI |
| Auth | JWT access token (30 min) + refresh token (7 days) |
| RBAC | 3 roles enforced at API level, not just UI |
| CORS | Explicit allowlist — no wildcard in production |
| SQL | SQLAlchemy ORM — no raw string queries |
| Secrets | Environment variables only — no hardcoded values |

---

## 📊 ML Features

| Engine | Algorithm | Metric |
|--------|-----------|--------|
| Demand Forecasting | XGBoost (28 features) | ~19% MAPE, 23% vs naive |
| Cost Optimization | EOQ + Safety Stock | avg $26K annual savings |
| Anomaly Detection | Isolation Forest (per-product) | z-score severity: high/medium/low |
| AI Chat | Claude Sonnet + RAG | grounded in live inventory data |

---

## 📁 Structure

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
│   └── Dockerfile
└── frontend/
    ├── src/
    │   ├── components/  layout · ui · charts
    │   ├── pages/       Login · Dashboard · Forecasting · Optimization · Anomalies · Products · Upload · AI · About
    │   ├── services/    Axios API client with auto-refresh
    │   └── store/       Zustand auth store (persisted)
    ├── package.json
    └── vercel.json
```
