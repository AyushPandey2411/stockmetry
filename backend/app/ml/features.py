"""app/ml/features.py — Feature engineering for demand forecasting."""
import numpy as np
import pandas as pd
from typing import List


LAG_DAYS       = [1, 3, 7, 14, 21, 28]
ROLL_WINDOWS   = [7, 14, 28]
FEATURE_COLS   = (
    [f"lag_{d}" for d in LAG_DAYS]
    + [f"rm_{w}" for w in ROLL_WINDOWS]
    + [f"rs_{w}" for w in ROLL_WINDOWS]
    + [f"ewm_{w}" for w in ROLL_WINDOWS]
    + ["dow_sin", "dow_cos", "doy_sin", "doy_cos",
       "is_wknd", "month", "quarter", "prod_code"]
)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Input:  df with columns [date, product_id, demand] — sorted by (product_id, date)
    Output: df with 28 feature columns appended, NaN rows dropped.
    """
    df = df.copy().sort_values(["product_id", "date"])
    grp = df.groupby("product_id")["demand"]

    # Lag features
    for d in LAG_DAYS:
        df[f"lag_{d}"] = grp.shift(d)

    # Rolling statistics
    for w in ROLL_WINDOWS:
        df[f"rm_{w}"] = grp.transform(lambda x: x.shift(1).rolling(w, min_periods=1).mean())
        df[f"rs_{w}"] = grp.transform(lambda x: x.shift(1).rolling(w, min_periods=1).std().fillna(0))
        df[f"ewm_{w}"] = grp.transform(lambda x: x.shift(1).ewm(span=w, min_periods=1).mean())

    # Cyclical time encodings
    doy = df["date"].dt.dayofyear
    dow = df["date"].dt.dayofweek
    df["dow_sin"] = np.sin(2 * np.pi * dow / 7)
    df["dow_cos"] = np.cos(2 * np.pi * dow / 7)
    df["doy_sin"] = np.sin(2 * np.pi * doy / 365.25)
    df["doy_cos"] = np.cos(2 * np.pi * doy / 365.25)
    df["is_wknd"] = (dow >= 5).astype(int)
    df["month"]   = df["date"].dt.month
    df["quarter"] = df["date"].dt.quarter
    df["prod_code"] = df["product_id"].astype("category").cat.codes

    df = df.dropna(subset=FEATURE_COLS)
    return df
