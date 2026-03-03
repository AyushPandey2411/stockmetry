"""app/models/forecast.py"""
from sqlalchemy import Column, Integer, Float, Date, DateTime, ForeignKey, String
from sqlalchemy.sql import func
from ..core.database import Base


class ForecastRecord(Base):
    __tablename__ = "forecasts"
    id         = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), index=True)
    date       = Column(Date, nullable=False)
    forecast   = Column(Float, nullable=False)
    ci_lower   = Column(Float, nullable=False)
    ci_upper   = Column(Float, nullable=False)
    model_ver  = Column(String(50), default="xgb_v1")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
