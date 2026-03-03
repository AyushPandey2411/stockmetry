"""app/models/anomaly.py"""
from sqlalchemy import Column, Integer, Float, Date, DateTime, ForeignKey, String, Boolean
from sqlalchemy.sql import func
from ..core.database import Base


class AnomalyRecord(Base):
    __tablename__ = "anomalies"
    id          = Column(Integer, primary_key=True)
    product_id  = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), index=True)
    date        = Column(Date, nullable=False)
    demand      = Column(Float, nullable=False)
    avg_demand  = Column(Float, nullable=False)
    z_score     = Column(Float, nullable=False)
    anomaly_type = Column(String(20), default="unusual")   # spike | drop | unusual
    severity    = Column(String(10), default="low")        # high | medium | low
    is_reviewed = Column(Boolean, default=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
