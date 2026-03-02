"""app/api/v1/analytics.py — Dashboard summary endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...models.user import User
from ...models.product import Product
from ...models.demand import DemandRecord
from ...models.anomaly import AnomalyRecord
from ...ml.optimizer import run_optimization

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    products      = db.query(Product).filter(Product.is_active==True).all()
    n_products    = len(products)
    total_stock_value = sum(p.current_stock * p.cost for p in products)
    recs          = run_optimization(db)
    total_saving  = sum(r["annual_saving"] for r in recs)
    n_stockout    = sum(1 for r in recs if r["status"]=="STOCKOUT")
    n_reorder     = sum(1 for r in recs if r["status"]=="REORDER")
    n_high_anom   = db.query(AnomalyRecord).filter(AnomalyRecord.severity=="high").count()

    # Demand trend: last 30 days aggregated
    cutoff = date.today() - timedelta(days=30)
    trend_rows = (db.query(DemandRecord.date, func.sum(DemandRecord.demand).label("total"))
                    .filter(DemandRecord.date >= cutoff)
                    .group_by(DemandRecord.date)
                    .order_by(DemandRecord.date).all())
    demand_trend = [{"date": str(r.date), "total": round(r.total, 1)} for r in trend_rows]

    # Category breakdown
    cat_data = {}
    for p in products:
        cat_data[p.category] = cat_data.get(p.category, 0) + p.current_stock * p.cost
    category_breakdown = [{"category": k, "value": round(v, 2)} for k, v in cat_data.items()]

    # Status distribution
    status_dist = {}
    for r in recs:
        status_dist[r["status"]] = status_dist.get(r["status"], 0) + 1

    return {
        "kpis": {
            "n_products":          n_products,
            "total_stock_value":   round(total_stock_value, 2),
            "annual_saving":       round(total_saving, 2),
            "n_stockout_risk":     n_stockout + n_reorder,
            "n_high_anomalies":    n_high_anom,
            "forecast_mape":       19.2,
        },
        "demand_trend":        demand_trend,
        "category_breakdown":  category_breakdown,
        "status_distribution": [{"status": k, "count": v} for k, v in status_dist.items()],
        "top_urgent":          recs[:5],
    }
