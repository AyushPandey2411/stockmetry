"""app/api/v1/forecasts.py"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
import pandas as pd
from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...models.user import User
from ...models.demand import DemandRecord
from ...models.forecast import ForecastRecord
from ...models.product import Product
from ...ml.forecaster import forecast as run_forecast

router = APIRouter(prefix="/forecasts", tags=["Forecasting"])


@router.get("/")
def get_forecasts(
    product_id: Optional[int] = Query(None),
    horizon: int = Query(30, ge=7, le=90),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    # Historical (last 90 days)
    from datetime import date, timedelta
    cutoff = date.today() - timedelta(days=90)
    hist_q = db.query(DemandRecord, Product.name, Product.sku).join(
        Product, Product.id == DemandRecord.product_id
    ).filter(DemandRecord.date >= cutoff)
    if product_id:
        hist_q = hist_q.filter(DemandRecord.product_id == product_id)
    historical = [{"date": str(r.DemandRecord.date), "demand": r.DemandRecord.demand,
                    "product_id": r.DemandRecord.product_id, "name": r.name} for r in hist_q.all()]

    # Forecasts from DB
    fc_q = db.query(ForecastRecord, Product.name, Product.sku).join(
        Product, Product.id == ForecastRecord.product_id
    ).filter(ForecastRecord.date >= date.today())
    if product_id:
        fc_q = fc_q.filter(ForecastRecord.product_id == product_id)
    forecasts = [{"date": str(r.ForecastRecord.date), "forecast": r.ForecastRecord.forecast,
                   "ci_lower": r.ForecastRecord.ci_lower, "ci_upper": r.ForecastRecord.ci_upper,
                   "product_id": r.ForecastRecord.product_id, "name": r.name} for r in fc_q.limit(horizon * 50).all()]

    products = [{"id": p.id, "name": p.name, "sku": p.sku}
                for p in db.query(Product).filter(Product.is_active == True).all()]
    return {"historical": historical, "forecasts": forecasts, "products": products}


@router.post("/retrain")
def retrain(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Re-run forecast model and refresh DB forecast records."""
    rows = db.query(DemandRecord).all()
    if not rows:
        return {"error": "No demand data available"}
    df = pd.DataFrame([{"product_id": r.product_id, "date": r.date, "demand": r.demand} for r in rows])
    product_ids = df["product_id"].unique().tolist()
    fc_df = run_forecast(df, product_ids, horizon=30)
    # Clear old forecasts and insert new
    db.query(ForecastRecord).delete()
    for _, row in fc_df.iterrows():
        db.add(ForecastRecord(product_id=int(row["product_id"]), date=row["date"],
                               forecast=row["forecast"], ci_lower=row["ci_lower"], ci_upper=row["ci_upper"]))
    db.commit()
    return {"message": f"Forecast refreshed for {len(product_ids)} products"}
