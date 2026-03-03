"""app/models/demand.py"""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..core.database import Base


class DemandRecord(Base):
    __tablename__ = "demand_history"
    id         = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), index=True)
    date       = Column(Date, nullable=False, index=True)
    demand     = Column(Float, nullable=False)
    source     = Column(String(50), default="synthetic")  # synthetic | uploaded | actual
    created_at = Column(DateTime(timezone=True), server_default=func.now())
