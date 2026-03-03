"""app/models/product.py"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from ..core.database import Base


class Product(Base):
    __tablename__ = "products"

    id              = Column(Integer, primary_key=True, index=True)
    sku             = Column(String(50),  unique=True, index=True, nullable=False)
    name            = Column(String(255), nullable=False)
    category        = Column(String(100), nullable=False)
    unit            = Column(String(50),  default="units")
    price           = Column(Float,  nullable=False)
    cost            = Column(Float,  nullable=False)          # Purchase cost per unit
    ordering_cost   = Column(Float,  default=50.0)            # Cost per order (S)
    holding_rate    = Column(Float,  default=0.25)            # Annual holding rate (h)
    lead_time_days  = Column(Integer, default=7)
    reorder_point   = Column(Float,  default=0.0)
    safety_stock    = Column(Float,  default=0.0)
    current_stock   = Column(Float,  default=0.0)
    min_stock       = Column(Float,  default=0.0)
    max_stock       = Column(Float,  default=10000.0)
    supplier        = Column(String(255), default="")
    warehouse_zone  = Column(String(20),  default="A1")
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())
