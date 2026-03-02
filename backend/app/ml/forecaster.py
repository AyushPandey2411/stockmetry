"""app/ml/forecaster.py — XGBoost demand forecasting."""
import os
import numpy as np
import pandas as pd
import joblib
from typing import Dict, List, Tuple
from datetime import date, timedelta

try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except ImportError:
    from sklearn.linear_model import Ridge
    HAS_XGB = False

from sklearn.metrics import mean_absolute_percentage_error
from .features import build_features, FEATURE_COLS

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "models", "forecaster.pkl")


def train(df: pd.DataFrame) -> Tuple[object, dict]:
    """
    Train XGBoost on demand data.
    Returns (model, metrics_dict).
    """
    df["date"] = pd.to_datetime(df["date"])
    feat_df = build_features(df)

    # Chronological split — last 15% as test
    split = int(len(feat_df) * 0.85)
    train_df = feat_df.iloc[:split]
    test_df  = feat_df.iloc[split:]

    X_train, y_train = train_df[FEATURE_COLS].values, train_df["demand"].values
    X_test,  y_test  = test_df[FEATURE_COLS].values,  test_df["demand"].values

    if HAS_XGB:
        model = XGBRegressor(
            n_estimators=400, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            objective="reg:squarederror", random_state=42,
            n_jobs=-1, verbosity=0,
        )
    else:
        from sklearn.linear_model import Ridge
        model = Ridge(alpha=1.0)

    model.fit(X_train, y_train)
    preds = np.maximum(0, model.predict(X_test))

    # Naive baseline: lag-7
    naive = test_df["lag_7"].values
    xgb_mape   = mean_absolute_percentage_error(y_test, preds)       * 100
    naive_mape = mean_absolute_percentage_error(y_test, naive)        * 100
    improvement = ((naive_mape - xgb_mape) / naive_mape)              * 100

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    return model, {
        "model_type":   "XGBoost" if HAS_XGB else "Ridge",
        "xgb_mape":     round(xgb_mape, 2),
        "naive_mape":   round(naive_mape, 2),
        "improvement":  round(improvement, 2),
        "train_rows":   len(train_df),
        "test_rows":    len(test_df),
    }


def forecast(
    df: pd.DataFrame,
    product_ids: List[int],
    horizon: int = 30,
) -> pd.DataFrame:
    """
    Produce rolling horizon-day forecast for each product.
    Returns DataFrame with [product_id, date, forecast, ci_lower, ci_upper].
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model not trained yet. Run seed.py first.")

    model  = joblib.load(MODEL_PATH)
    df     = df.copy()
    df["date"] = pd.to_datetime(df["date"])

    all_rows = []
    for pid in product_ids:
        pdata = df[df["product_id"] == pid].copy().sort_values("date")
        if len(pdata) < 30:
            continue

        # Estimate per-product demand std for CI
        sigma = pdata["demand"].rolling(30).std().iloc[-1]
        if np.isnan(sigma):
            sigma = pdata["demand"].std()

        last_date = pdata["date"].max()
        rolling   = pdata.copy()

        for step in range(1, horizon + 1):
            next_date = last_date + timedelta(days=step)
            tmp = pd.concat([rolling, pd.DataFrame([{
                "product_id": pid, "date": next_date, "demand": 0
            }])], ignore_index=True)
            feat_row = build_features(tmp).iloc[[-1]]
            if feat_row.empty:
                break
            X = feat_row[FEATURE_COLS].values
            fc_val = float(max(0, model.predict(X)[0]))
            ci_hw  = 1.96 * sigma * np.sqrt(step * 0.15)

            all_rows.append({
                "product_id": pid,
                "date":       next_date.date(),
                "forecast":   round(fc_val, 1),
                "ci_lower":   round(max(0, fc_val - ci_hw), 1),
                "ci_upper":   round(fc_val + ci_hw, 1),
            })
            # Add predicted value back for next iteration
            new_row = {"product_id": pid, "date": next_date, "demand": fc_val}
            rolling = pd.concat([rolling, pd.DataFrame([new_row])], ignore_index=True)

    return pd.DataFrame(all_rows)
