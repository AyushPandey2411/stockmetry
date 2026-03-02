"""app/api/v1/optimize.py"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...models.user import User
from ...ml.optimizer import run_optimization

router = APIRouter(prefix="/optimize", tags=["Optimization"])

@router.get("/")
def get_optimization(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    results = run_optimization(db)
    total_saving = sum(r["annual_saving"] for r in results)
    avg_pct      = sum(r["pct_saving"] for r in results) / len(results) if results else 0
    status_counts = {}
    for r in results:
        status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1
    return {
        "recommendations": results,
        "summary": {
            "total_annual_saving": round(total_saving, 2),
            "avg_pct_saving": round(avg_pct, 1),
            "status_counts": status_counts,
            "n_products": len(results),
        }
    }
