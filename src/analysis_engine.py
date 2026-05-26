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
    required = {"rsi_14", "macd", "macd_signal", "sma_20", "sma_50", "close"}
    if not isinstance(df, pd.DataFrame) or df.empty or not required.issubset(df.columns):
        return "HOLD"

    clean = df.dropna(subset=list(required))
    if len(clean) < 2:
        return "HOLD"

    row = clean.iloc[-1]
    prev = clean.iloc[-2]

    rsi = float(row["rsi_14"])
    macd = float(row["macd"])
    macd_sig = float(row["macd_signal"])
    prev_macd = float(prev["macd"])
    prev_macd_sig = float(prev["macd_signal"])
    sma20 = float(row["sma_20"])
    sma50 = float(row["sma_50"])
    close = float(row["close"])

    bullish_score = 0
    bearish_score = 0

    # Momentum regime
    if rsi <= 45:
        bullish_score += 1
    elif rsi >= 55:
        bearish_score += 1

    # MACD crossover regime
    macd_cross_up = prev_macd <= prev_macd_sig and macd > macd_sig
    macd_cross_down = prev_macd >= prev_macd_sig and macd < macd_sig
    if macd_cross_up or macd > macd_sig:
        bullish_score += 1
    if macd_cross_down or macd < macd_sig:
        bearish_score += 1

    # Trend regime
    if sma20 > sma50 and close >= sma20:
        bullish_score += 1
    if sma20 < sma50 and close <= sma20:
        bearish_score += 1

    if bullish_score >= 2 and bullish_score > bearish_score:
        return "BUY"
    if bearish_score >= 2 and bearish_score > bullish_score:
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
    if len(close) < 25:
        return None

    # Adapt feature windows for shorter history windows (e.g., 1mo)
    w_sma_fast = 5 if len(close) < 60 else 10
    w_sma_slow = 10 if len(close) < 60 else 20
    w_mom = 3 if len(close) < 60 else 5
    w_vol = 5 if len(close) < 60 else 10

    feat = pd.DataFrame(index=close.index)
    feat["close"] = close
    feat["sma_fast"] = close.rolling(w_sma_fast).mean()
    feat["sma_slow"] = close.rolling(w_sma_slow).mean()
    feat["momentum"] = close.pct_change(w_mom)
    feat["volatility"] = close.pct_change().rolling(w_vol).std()
    feat["target"] = close.shift(-1)
    feat = feat.dropna()

    min_required = 18 if len(close) < 60 else max(40, lookback)
    if len(feat) < min_required:
        return None

    X = feat[["close", "sma_fast", "sma_slow", "momentum", "volatility"]]
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

    effective_lookback = min(lookback, len(close))
    latest_close = close.iloc[-effective_lookback:]

    latest_frame = pd.DataFrame(index=latest_close.index)
    latest_frame["close"] = latest_close
    latest_frame["sma_fast"] = latest_close.rolling(w_sma_fast).mean()
    latest_frame["sma_slow"] = latest_close.rolling(w_sma_slow).mean()
    latest_frame["momentum"] = latest_close.pct_change(w_mom)
    latest_frame["volatility"] = latest_close.pct_change().rolling(w_vol).std()
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
