"""app/ml/optimizer.py — Economic Order Quantity optimization engine."""
import math
import numpy as np
import pandas as pd
from typing import List, Dict
from sqlalchemy.orm import Session
from ..models.product import Product
from ..models.demand import DemandRecord


def compute_eoq(annual_demand: float, ordering_cost: float, holding_cost_per_unit: float) -> float:
    """Wilson EOQ formula: Q* = sqrt(2DS/H)"""
    if holding_cost_per_unit <= 0 or annual_demand <= 0:
        return 0.0
    return math.sqrt((2 * annual_demand * ordering_cost) / holding_cost_per_unit)


def run_optimization(db: Session) -> List[Dict]:
    """Compute EOQ recommendations for all active products."""
    products = db.query(Product).filter(Product.is_active == True).all()
    results  = []

    for p in products:
        # Fetch last 365 days of demand
        from datetime import date, timedelta
        cutoff = date.today() - timedelta(days=365)
        rows = (db.query(DemandRecord)
                  .filter(DemandRecord.product_id == p.id,
                          DemandRecord.date >= cutoff)
                  .all())
        demands = [r.demand for r in rows]
        if not demands:
            continue

        avg_daily     = float(np.mean(demands))
        std_daily     = float(np.std(demands)) if len(demands) > 1 else avg_daily * 0.15
        annual_demand = avg_daily * 365

        # Costs
        H = p.price * p.holding_rate          # Annual holding cost per unit
        S = p.ordering_cost

        # EOQ & derived quantities
        eoq_qty     = max(1.0, round(compute_eoq(annual_demand, S, H)))
        safety_stk  = round(1.645 * std_daily * math.sqrt(p.lead_time_days), 1)
        rop         = round(avg_daily * p.lead_time_days + safety_stk, 1)
        days_stock  = round(p.current_stock / avg_daily, 1) if avg_daily > 0 else 999

        # Cost comparison: naive = order every 30 days
        orders_naive = annual_demand / (avg_daily * 30)
        orders_eoq   = annual_demand / eoq_qty
        naive_cost   = orders_naive * S + (avg_daily * 30 / 2) * H
        eoq_cost     = orders_eoq   * S + (eoq_qty          / 2) * H
        saving       = max(0.0, naive_cost - eoq_cost)
        pct_saving   = round((saving / naive_cost * 100) if naive_cost > 0 else 0, 1)

        # Status
        if p.current_stock <= 0:
            status = "STOCKOUT"
        elif p.current_stock <= rop:
            status = "REORDER"
        elif days_stock < p.lead_time_days:
            status = "LOW"
        elif p.current_stock > 4 * rop:
            status = "OVERSTOCK"
        else:
            status = "HEALTHY"

        # Persist reorder_point and safety_stock back to product
        p.reorder_point = rop
        p.safety_stock  = safety_stk

        results.append({
            "product_id":       p.id,
            "sku":              p.sku,
            "name":             p.name,
            "category":         p.category,
            "current_stock":    round(p.current_stock, 1),
            "avg_daily_demand": round(avg_daily, 2),
            "eoq":              eoq_qty,
            "reorder_point":    rop,
            "safety_stock":     safety_stk,
            "days_of_stock":    days_stock,
            "lead_time_days":   p.lead_time_days,
            "annual_demand":    round(annual_demand, 0),
            "naive_annual_cost": round(naive_cost, 2),
            "eoq_annual_cost":  round(eoq_cost, 2),
            "annual_saving":    round(saving, 2),
            "pct_saving":       pct_saving,
            "status":           status,
        })

    db.commit()
    return sorted(results, key=lambda r: {"STOCKOUT":0,"REORDER":1,"LOW":2,"HEALTHY":3,"OVERSTOCK":4}.get(r["status"],5))
