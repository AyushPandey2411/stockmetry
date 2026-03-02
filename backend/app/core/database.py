"""app/core/database.py — SQLAlchemy async-compatible PostgreSQL setup."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings

# Use sync engine for simplicity (fully compatible with Render/Supabase)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,          # Detect stale connections
    pool_size=10,                 # Connection pool size
    max_overflow=20,              # Extra connections under load
    pool_recycle=3600,            # Recycle connections every hour
    connect_args=(
        {"sslmode": "require"} if settings.is_production else {}
    ),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency — yields DB session, guarantees cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables. Called at startup."""
    from ..models import user, product, demand, forecast, anomaly  # noqa: F401
    Base.metadata.create_all(bind=engine)
