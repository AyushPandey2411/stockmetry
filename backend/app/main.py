"""app/main.py — Stockmetry FastAPI Application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from .core.config import settings
from .core.database import create_tables
from .api.v1 import auth, products, forecasts, optimize, anomalies, analytics, ai_chat, upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="Stockmetry API",
    description="AI-Powered Inventory Optimization Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# ── CORS ─────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────
PREFIX = "/api/v1"
app.include_router(auth.router,       prefix=PREFIX)
app.include_router(products.router,   prefix=PREFIX)
app.include_router(forecasts.router,  prefix=PREFIX)
app.include_router(optimize.router,   prefix=PREFIX)
app.include_router(anomalies.router,  prefix=PREFIX)
app.include_router(analytics.router,  prefix=PREFIX)
app.include_router(ai_chat.router,    prefix=PREFIX)
app.include_router(upload.router,     prefix=PREFIX)


@app.get("/health")
def health():
    return {"status": "ok", "version": settings.APP_VERSION, "app": settings.APP_NAME}
