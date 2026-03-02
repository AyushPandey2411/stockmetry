"""app/api/v1/anomalies.py"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...models.user import User
from ...models.anomaly import AnomalyRecord
from ...models.product import Product

router = APIRouter(prefix="/anomalies", tags=["Anomalies"])

@router.get("/")
def get_anomalies(
    severity: Optional[str] = Query(None),
    product_id: Optional[int] = Query(None),
    limit: int = Query(200),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(AnomalyRecord, Product.name, Product.sku).join(
        Product, Product.id == AnomalyRecord.product_id
    )
    if severity: q = q.filter(AnomalyRecord.severity == severity)
    if product_id: q = q.filter(AnomalyRecord.product_id == product_id)
    rows = q.order_by(AnomalyRecord.date.desc()).limit(limit).all()
    anomalies = [{
        "id": r.AnomalyRecord.id, "product_id": r.AnomalyRecord.product_id,
        "name": r.name, "sku": r.sku, "date": str(r.AnomalyRecord.date),
        "demand": r.AnomalyRecord.demand, "avg_demand": r.AnomalyRecord.avg_demand,
        "z_score": r.AnomalyRecord.z_score, "type": r.AnomalyRecord.anomaly_type,
        "severity": r.AnomalyRecord.severity, "is_reviewed": r.AnomalyRecord.is_reviewed,
    } for r in rows]
    total = db.query(AnomalyRecord).count()
    high  = db.query(AnomalyRecord).filter(AnomalyRecord.severity=="high").count()
    med   = db.query(AnomalyRecord).filter(AnomalyRecord.severity=="medium").count()
    return {"anomalies": anomalies, "summary": {"total": total, "high": high, "medium": med, "low": total-high-med}}

@router.patch("/{anomaly_id}/review")
def mark_reviewed(anomaly_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    a = db.query(AnomalyRecord).filter(AnomalyRecord.id == anomaly_id).first()
    if a:
        a.is_reviewed = True; db.commit()
    return {"ok": True}
