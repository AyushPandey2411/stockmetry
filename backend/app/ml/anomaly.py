"""app/ml/anomaly.py — Per-product Isolation Forest anomaly detection."""
import os
import numpy as np
import pandas as pd
import joblib
from typing import List, Dict
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")


def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Input: df with [product_id, date, demand]
    Returns DataFrame of anomaly records.
    """
    os.makedirs(MODELS_DIR, exist_ok=True)
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["product_id", "date"])

    # Rolling features for anomaly context
    grp = df.groupby("product_id")["demand"]
    df["lag_1"]  = grp.shift(1)
    df["lag_3"]  = grp.shift(3)
    df["lag_7"]  = grp.shift(7)
    df["rm_7"]   = grp.transform(lambda x: x.shift(1).rolling(7,  min_periods=1).mean())
    df["rm_14"]  = grp.transform(lambda x: x.shift(1).rolling(14, min_periods=1).mean())
    df["rs_7"]   = grp.transform(lambda x: x.shift(1).rolling(7,  min_periods=1).std().fillna(0))
    df["dow"]    = df["date"].dt.dayofweek
    df["month"]  = df["date"].dt.month
    df = df.dropna()

    FEAT = ["demand","lag_1","lag_3","lag_7","rm_7","rm_14","rs_7","dow","month"]
    anomaly_rows = []

    for pid, pdf in df.groupby("product_id"):
        if len(pdf) < 30:
            continue
        X = pdf[FEAT].values
        scaler = StandardScaler()
        Xs = scaler.fit_transform(X)
        iso = IsolationForest(n_estimators=100, contamination=0.05, random_state=42, n_jobs=-1)
        preds = iso.fit_predict(Xs)

        # Save per-product model
        path = os.path.join(MODELS_DIR, f"iso_{pid}.pkl")
        joblib.dump({"model": iso, "scaler": scaler}, path)

        anom_idx = pdf.index[preds == -1]
        for idx in anom_idx:
            row  = pdf.loc[idx]
            avg  = float(pdf["rm_14"].loc[idx])
            std  = float(pdf["rs_7"].loc[idx]) or 1e-6
            z    = round((row["demand"] - avg) / std, 2)
            absz = abs(z)
            sev  = "high" if absz > 3.5 else ("medium" if absz > 3.0 else "low")
            typ  = ("spike" if row["demand"] > avg * 1.5
                    else ("drop" if row["demand"] < avg * 0.5 else "unusual"))
            anomaly_rows.append({
                "product_id":   int(pid),
                "date":         row["date"].date(),
                "demand":       round(float(row["demand"]), 1),
                "avg_demand":   round(avg, 1),
                "z_score":      z,
                "anomaly_type": typ,
                "severity":     sev,
            })

    return pd.DataFrame(anomaly_rows)
