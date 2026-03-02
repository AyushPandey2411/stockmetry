"""app/schemas/product.py"""
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class ProductBase(BaseModel):
    sku: str
    name: str
    category: str
    unit: str = "units"
    price: float
    cost: float
    ordering_cost: float = 50.0
    holding_rate: float = 0.25
    lead_time_days: int = 7
    current_stock: float = 0.0
    supplier: str = ""
    warehouse_zone: str = "A1"


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    cost: Optional[float] = None
    current_stock: Optional[float] = None
    ordering_cost: Optional[float] = None
    holding_rate: Optional[float] = None
    lead_time_days: Optional[int] = None
    supplier: Optional[str] = None
    warehouse_zone: Optional[str] = None


class ProductOut(ProductBase):
    id: int
    reorder_point: float
    safety_stock: float
    min_stock: float
    max_stock: float
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class EOQResult(BaseModel):
    product_id: int
    sku: str
    name: str
    category: str
    current_stock: float
    avg_daily_demand: float
    eoq: float
    reorder_point: float
    safety_stock: float
    days_of_stock: float
    lead_time_days: int
    annual_demand: float
    naive_annual_cost: float
    eoq_annual_cost: float
    annual_saving: float
    pct_saving: float
    status: str   # STOCKOUT | REORDER | LOW | HEALTHY | OVERSTOCK
