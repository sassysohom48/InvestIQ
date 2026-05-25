from __future__ import annotations

from typing import Dict, Optional

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error


def _validate_price_df(df: pd.DataFrame) -> bool:
    return isinstance(df, pd.DataFrame) and not df.empty and "close" in df.columns


def _compute_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def apply_indicators(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    if not _validate_price_df(df):
        return None

    out = df.copy()
    close = out["close"].astype(float)

    out["sma_20"] = close.rolling(window=20, min_periods=20).mean()
    out["sma_50"] = close.rolling(window=50, min_periods=50).mean()
    out["rsi_14"] = _compute_rsi(close, period=14)

    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    out["macd"] = ema_12 - ema_26
    out["macd_signal"] = out["macd"].ewm(span=9, adjust=False).mean()
    out["macd_hist"] = out["macd"] - out["macd_signal"]

    return out


def generate_signal(df: pd.DataFrame) -> str:
    if not isinstance(df, pd.DataFrame) or df.empty or "rsi_14" not in df.columns:
        return "HOLD"

    latest_rsi = df["rsi_14"].dropna()
    if latest_rsi.empty:
        return "HOLD"

    value = float(latest_rsi.iloc[-1])
    if value < 30:
        return "BUY"
    if value > 70:
        return "SELL"
    return "HOLD"


def calculate_position_size(
    capital: float,
    risk_pct: float,
    stop_loss: float,
    current_price: float,
) -> Dict[str, float]:
    if capital <= 0 or risk_pct <= 0 or current_price <= 0 or stop_loss <= 0:
        return {"shares": 0, "risk_amount": 0.0, "position_value": 0.0}

    risk_amount = capital * (risk_pct / 100.0)
    risk_per_share = abs(current_price - stop_loss)
    if risk_per_share <= 0:
        return {"shares": 0, "risk_amount": float(risk_amount), "position_value": 0.0}

    shares_by_risk = int(risk_amount // risk_per_share)
    shares_by_capital = int(capital // current_price)
    shares = max(0, min(shares_by_risk, shares_by_capital))
    position_value = shares * current_price

    return {
        "shares": float(shares),
        "risk_amount": float(risk_amount),
        "position_value": float(position_value),
    }


def predict_price(
    df: pd.DataFrame,
    lookback: int = 60,
    test_size: float = 0.2,
) -> Optional[Dict[str, float]]:
    if not _validate_price_df(df):
        return None
    if lookback < 5 or not (0.05 <= test_size <= 0.5):
        return None

    close = df["close"].astype(float).copy()
    feat = pd.DataFrame(index=close.index)
    feat["close"] = close
    feat["sma_10"] = close.rolling(10).mean()
    feat["sma_20"] = close.rolling(20).mean()
    feat["momentum_5"] = close.pct_change(5)
    feat["volatility_10"] = close.pct_change().rolling(10).std()
    feat["target"] = close.shift(-1)
    feat = feat.dropna()

    if len(feat) < max(40, lookback):
        return None

    X = feat[["close", "sma_10", "sma_20", "momentum_5", "volatility_10"]]
    y = feat["target"]

    split_idx = int(len(feat) * (1 - test_size))
    if split_idx <= 0 or split_idx >= len(feat):
        return None

    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    if X_test.empty:
        return None

    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred_test = model.predict(X_test)
    mae = float(mean_absolute_error(y_test, y_pred_test))

    latest_close = close.iloc[-lookback:]
    if len(latest_close) < lookback:
        return None

    latest_frame = pd.DataFrame(index=latest_close.index)
    latest_frame["close"] = latest_close
    latest_frame["sma_10"] = latest_close.rolling(10).mean()
    latest_frame["sma_20"] = latest_close.rolling(20).mean()
    latest_frame["momentum_5"] = latest_close.pct_change(5)
    latest_frame["volatility_10"] = latest_close.pct_change().rolling(10).std()
    latest_row = latest_frame.dropna().iloc[[-1]]
    if latest_row.empty:
        return None

    next_close_pred = float(model.predict(latest_row)[0])
    current_close = float(close.iloc[-1])
    error_pct = float((mae / current_close) * 100) if current_close != 0 else 0.0

    return {
        "predicted_close": next_close_pred,
        "mae": mae,
        "mae_pct_of_price": error_pct,
        "train_rows": float(len(X_train)),
        "test_rows": float(len(X_test)),
    }
