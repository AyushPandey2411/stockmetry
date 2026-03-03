#!/usr/bin/env python3
"""
seed.py — Stockmetry database seeder + ML model trainer.
Run: python seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import math
import numpy as np
import pandas as pd
from datetime import date, timedelta
from pathlib import Path

# Ensure backend root is on path
sys.path.insert(0, str(Path(__file__).parent))

os.makedirs("models", exist_ok=True)

from app.core.database import SessionLocal, create_tables
from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User
from app.models.product import Product
from app.models.demand import DemandRecord
from app.models.forecast import ForecastRecord
from app.models.anomaly import AnomalyRecord


def seed_users(db):
    users = [
        {"email":"admin@stockmetry.io",   "username":"admin",   "full_name":"Ayush Kumar",  "role":"admin",   "password":settings.ADMIN_PASSWORD,   "avatar_color":"#6366f1"},
        {"email":"manager@stockmetry.io", "username":"manager", "full_name":"Priya Sharma", "role":"manager", "password":settings.MANAGER_PASSWORD, "avatar_color":"#10b981"},
        {"email":"analyst@stockmetry.io", "username":"analyst", "full_name":"Rohan Mehta",  "role":"analyst", "password":settings.ANALYST_PASSWORD,  "avatar_color":"#f59e0b"},
    ]
    created = 0
    for u in users:
        if not db.query(User).filter(User.email == u["email"]).first():
            db.add(User(email=u["email"], username=u["username"], full_name=u["full_name"],
                        role=u["role"], hashed_password=hash_password(u["password"]),
                        avatar_color=u["avatar_color"]))
            created += 1
    db.commit()
    print(f"  Users: {created} created")


PRODUCTS = [
    {"sku":"P001","name":"Wireless Headphones",   "category":"Electronics",  "price":89.99, "cost":42.0,  "ordering_cost":60,"holding_rate":0.25,"lead_time_days":7,  "current_stock":380,"base_demand":42},
    {"sku":"P002","name":"Running Shoes",          "category":"Footwear",     "price":119.99,"cost":55.0,  "ordering_cost":80,"holding_rate":0.22,"lead_time_days":10, "current_stock":42, "base_demand":28},
    {"sku":"P003","name":"Yoga Mat",               "category":"Sports",       "price":34.99, "cost":12.0,  "ordering_cost":35,"holding_rate":0.30,"lead_time_days":5,  "current_stock":290,"base_demand":35},
    {"sku":"P004","name":"Air Purifier",           "category":"Appliances",   "price":199.99,"cost":95.0,  "ordering_cost":90,"holding_rate":0.20,"lead_time_days":14, "current_stock":95, "base_demand":18},
    {"sku":"P005","name":"Smart Watch",            "category":"Electronics",  "price":249.99,"cost":120.0, "ordering_cost":75,"holding_rate":0.25,"lead_time_days":8,  "current_stock":0,  "base_demand":22},
    {"sku":"P006","name":"Water Bottle",           "category":"Accessories",  "price":19.99, "cost":5.5,   "ordering_cost":25,"holding_rate":0.35,"lead_time_days":4,  "current_stock":520,"base_demand":65},
    {"sku":"P007","name":"Running Shorts",         "category":"Clothing",     "price":44.99, "cost":18.0,  "ordering_cost":40,"holding_rate":0.28,"lead_time_days":6,  "current_stock":160,"base_demand":30},
    {"sku":"P008","name":"Mechanical Keyboard",   "category":"Home Office",  "price":149.99,"cost":68.0,  "ordering_cost":55,"holding_rate":0.23,"lead_time_days":9,  "current_stock":88, "base_demand":15},
    {"sku":"P009","name":"Winter Jacket",          "category":"Clothing",     "price":129.99,"cost":58.0,  "ordering_cost":70,"holding_rate":0.22,"lead_time_days":12, "current_stock":45, "base_demand":20},
    {"sku":"P010","name":"Protein Powder",         "category":"Nutrition",    "price":59.99, "cost":22.0,  "ordering_cost":45,"holding_rate":0.32,"lead_time_days":5,  "current_stock":210,"base_demand":48},
    {"sku":"P011","name":"Laptop Stand",           "category":"Home Office",  "price":79.99, "cost":28.0,  "ordering_cost":40,"holding_rate":0.28,"lead_time_days":6,  "current_stock":145,"base_demand":25},
    {"sku":"P012","name":"Resistance Bands Set",   "category":"Sports",       "price":24.99, "cost":8.0,   "ordering_cost":28,"holding_rate":0.33,"lead_time_days":4,  "current_stock":330,"base_demand":52},
]


def seed_products(db):
    created = 0
    id_map = {}
    for pd_data in PRODUCTS:
        p = db.query(Product).filter(Product.sku == pd_data["sku"]).first()
        if not p:
            p = Product(sku=pd_data["sku"], name=pd_data["name"], category=pd_data["category"],
                        price=pd_data["price"], cost=pd_data["cost"],
                        ordering_cost=pd_data["ordering_cost"], holding_rate=pd_data["holding_rate"],
                        lead_time_days=pd_data["lead_time_days"], current_stock=pd_data["current_stock"],
                        unit="units", supplier="Stockmetry Suppliers Ltd", warehouse_zone="A1")
            db.add(p); db.flush(); created += 1
        id_map[pd_data["sku"]] = p.id
    db.commit()
    print(f"  Products: {created} created")
    return id_map


def generate_demand(db, id_map):
    # Clear existing synthetic demand
    db.query(DemandRecord).filter(DemandRecord.source=="synthetic").delete()
    db.commit()

    rows = []
    end_date  = date.today()
    start_date = end_date - timedelta(days=730)
    dates = pd.date_range(start_date, end_date)
    rng = np.random.default_rng(42)

    for pd_data in PRODUCTS:
        pid  = id_map[pd_data["sku"]]
        base = pd_data["base_demand"]
        for dt in dates:
            doy = dt.day_of_year
            dow = dt.day_of_week
            weekly   = 1 + 0.15 * math.sin(2 * math.pi * dow / 7)
            annual   = 1 + 0.20 * math.sin(2 * math.pi * (doy - 80) / 365.25)
            days     = (dt - pd.Timestamp(start_date)).days
            trend    = 1 + 0.15 * (days / 730)
            noise    = rng.normal(1, 0.12)

            # Seasonal spikes
            spike = 1.0
            if dt.month == 11 and dt.day >= 25: spike = 2.8   # Black Friday
            if dt.month == 12 and dt.day >= 20: spike = 1.6   # Christmas

            # Random events
            if rng.random() < 0.025: spike *= rng.uniform(2.5, 4.5)
            if rng.random() < 0.020: spike *= 0.05

            d = max(0.0, round(base * weekly * annual * trend * noise * spike, 1))
            rows.append(DemandRecord(product_id=pid, date=dt.date(), demand=d, source="synthetic"))

    db.bulk_save_objects(rows)
    db.commit()
    print(f"  Demand: {len(rows)} records seeded")
    return rows


def train_models(db):
    print("\n  Training ML models...")
    from app.models.demand import DemandRecord as DR
    rows = db.query(DR).all()
    df = pd.DataFrame([{"product_id":r.product_id,"date":r.date,"demand":r.demand} for r in rows])

    # Forecaster
    from app.ml.forecaster import train, forecast as run_fc
    model, metrics = train(df)
    print(f"    XGBoost MAPE: {metrics['xgb_mape']}% | Improvement: {metrics['improvement']}%")

    # Forecasts
    pid_list = df["product_id"].unique().tolist()
    fc_df = run_fc(df, pid_list, horizon=30)
    db.query(ForecastRecord).delete()
    for _, row in fc_df.iterrows():
        db.add(ForecastRecord(product_id=int(row["product_id"]), date=row["date"],
                               forecast=row["forecast"], ci_lower=row["ci_lower"], ci_upper=row["ci_upper"]))
    print(f"    Forecasts: {len(fc_df)} records saved")

    # Anomaly detection
    from app.ml.anomaly import detect_anomalies
    anom_df = detect_anomalies(df)
    db.query(AnomalyRecord).delete()
    for _, row in anom_df.iterrows():
        db.add(AnomalyRecord(product_id=int(row["product_id"]), date=row["date"],
                              demand=row["demand"], avg_demand=row["avg_demand"],
                              z_score=row["z_score"], anomaly_type=row["anomaly_type"],
                              severity=row["severity"]))
    print(f"    Anomalies: {len(anom_df)} detected")
    db.commit()


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  Stockmetry — Database Seeder & Model Trainer")
    print("="*55)
    create_tables()
    db = SessionLocal()
    try:
        print("\n[1/4] Seeding users...")
        seed_users(db)
        print("[2/4] Seeding products...")
        id_map = seed_products(db)
        print("[3/4] Generating demand history...")
        generate_demand(db, id_map)
        print("[4/4] Training ML models...")
        train_models(db)
        print("\n✓ Seeding complete!")
        print(f"\n  Login: admin@stockmetry.io / {settings.ADMIN_PASSWORD}")
        print("  Start: uvicorn app.main:app --reload --port 8000\n")
    finally:
        db.close()
