"""app/api/v1/upload.py — CSV/XLSX file upload and ingestion."""
import io
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
from ...core.database import get_db
from ...core.dependencies import require_manager
from ...models.user import User
from ...models.demand import DemandRecord
from ...models.product import Product

router = APIRouter(prefix="/upload", tags=["Upload"])

REQUIRED_COLS = {"date", "product", "demand"}


@router.post("/demand")
async def upload_demand(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_manager),
):
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ("csv", "xlsx"):
        raise HTTPException(400, "Only CSV and XLSX files are supported")

    contents = await file.read()
    try:
        if ext == "csv":
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(400, f"Could not parse file: {e}")

    df.columns = [c.lower().strip() for c in df.columns]
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise HTTPException(400, f"Missing required columns: {missing}. Required: {REQUIRED_COLS}")

    df["date"] = pd.to_datetime(df["date"])
    inserted, skipped = 0, 0

    for _, row in df.iterrows():
        prod = db.query(Product).filter(
            (Product.sku == str(row["product"])) | (Product.name == str(row["product"]))
        ).first()
        if not prod:
            skipped += 1
            continue
        rec = DemandRecord(
            product_id=prod.id, date=row["date"].date(),
            demand=float(row["demand"]), source="uploaded"
        )
        db.add(rec)
        inserted += 1

    db.commit()
    return {"inserted": inserted, "skipped": skipped, "total_rows": len(df)}
