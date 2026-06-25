from __future__ import annotations

from typing import Dict, Optional

import numpy as np
import pandas as pd
import pandas_ta as ta
from sklearn.linear_model import Ridge
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, accuracy_score, f1_score, confusion_matrix, r2_score
import xgboost as xgb


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


def _build_features(df: pd.DataFrame) -> pd.DataFrame:
    close = df["close"].astype(float).copy()
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
    feat["rsi"] = ta.rsi(close, length=14)
    macd = ta.macd(close, fast=12, slow=26, signal=9)
    if macd is not None and not macd.empty:
        feat["macd"] = macd.iloc[:, 0]
        feat["macd_signal"] = macd.iloc[:, 1]
    feat["lag_return"] = close.pct_change(1).shift(1)
    
    bbands = ta.bbands(close, length=20)
    if bbands is not None and not bbands.empty:
        feat["bb_lower"] = bbands.iloc[:, 0]
        feat["bb_upper"] = bbands.iloc[:, 2]
        
    if "volume" in df.columns and "high" in df.columns and "low" in df.columns:
        vwap = ta.vwap(high=df["high"], low=df["low"], close=df["close"], volume=df["volume"])
        if vwap is not None and not vwap.empty:
            feat["vwap"] = vwap

    # Fetch Macro data
    import yfinance as yf
    try:
        start_dt = df.index.min().strftime('%Y-%m-%d')
        end_dt = (df.index.max() + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        
        vix = yf.download("^INDIAVIX", start=start_dt, end=end_dt, progress=False)["Close"]
        nse = yf.download("^NSEI", start=start_dt, end=end_dt, progress=False)["Close"]
        
        if isinstance(vix, pd.DataFrame): vix = vix.iloc[:, 0]
        if isinstance(nse, pd.DataFrame): nse = nse.iloc[:, 0]
        
        feat["vix"] = vix
        feat["nse_ret"] = nse.pct_change()
    except Exception:
        feat["vix"] = 15.0
        feat["nse_ret"] = 0.0

    feat["vix"] = feat["vix"].ffill().fillna(15.0)
    feat["nse_ret"] = feat["nse_ret"].ffill().fillna(0.0)

    # Extract the very last row for live prediction before shifting the target
    feat_for_latest = feat.dropna()
    latest_row = feat_for_latest.iloc[[-1]] if not feat_for_latest.empty else pd.DataFrame()
    
    feat["target"] = close.pct_change().shift(-1)
    feat = feat.dropna()
    return feat, latest_row

def predict_price(
    df: pd.DataFrame,
    lookback: int = 60,
    test_size: float = 0.2,
    model_type: str = "Linear Regression",
) -> Optional[Dict[str, float]]:
    if not _validate_price_df(df):
        return None
    if lookback < 5 or not (0.05 <= test_size <= 0.5):
        return None

    close = df["close"].astype(float).copy()
    if len(close) < 25:
        return None

    feat, latest_row = _build_features(df)

    min_required = 18 if len(close) < 60 else 30
    if len(feat) < min_required:
        return None

    X = feat.drop(columns=["target"])
    y = feat["target"]

    split_idx = int(len(feat) * (1 - test_size))
    if split_idx <= 0 or split_idx >= len(feat):
        return None

    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    if X_test.empty or latest_row.empty:
        return None
    
    rob_scaler = RobustScaler()
    X_train_scaled = rob_scaler.fit_transform(X_train)
    X_test_scaled = rob_scaler.transform(X_test)
    latest_row_scaled = rob_scaler.transform(latest_row)
    
    if model_type == "XGBoost":
        model = xgb.XGBRegressor(n_estimators=50, max_depth=3, reg_lambda=1.0, learning_rate=0.1, random_state=42)
        model.fit(X_train_scaled, y_train)
        y_pred_ret_test = model.predict(X_test_scaled)
        y_pred_test = X_test["close"].values * (1 + y_pred_ret_test)
        latest_ret_pred = float(model.predict(latest_row_scaled)[0])
        next_close_pred = float(latest_row["close"].iloc[0] * (1 + latest_ret_pred))
    elif model_type == "LSTM":
        import os
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
        import tensorflow as tf
        import random
        random.seed(42)
        np.random.seed(42)
        tf.random.set_seed(42)
        
        from tensorflow.keras.models import Model
        from tensorflow.keras.layers import Input, Conv1D, MaxPooling1D, LSTM, Dense, Dropout, Attention, GlobalAveragePooling1D
        from sklearn.preprocessing import MinMaxScaler
        
        scaler_y = MinMaxScaler()
        y_train_lstm_scaled = scaler_y.fit_transform(y_train.values.reshape(-1, 1))
        
        X_train_lstm = X_train_scaled.reshape((X_train_scaled.shape[0], X_train_scaled.shape[1], 1))
        X_test_lstm = X_test_scaled.reshape((X_test_scaled.shape[0], X_test_scaled.shape[1], 1))
        latest_row_lstm = latest_row_scaled.reshape((latest_row_scaled.shape[0], latest_row_scaled.shape[1], 1))
        
        inputs = Input(shape=(X_train_lstm.shape[1], X_train_lstm.shape[2]))
        x = Conv1D(filters=32, kernel_size=2, activation='relu')(inputs)
        x = MaxPooling1D(pool_size=2)(x)
        lstm_out = LSTM(50, activation='relu', return_sequences=True)(x)
        attn_out = Attention()([lstm_out, lstm_out])
        
        x = GlobalAveragePooling1D()(attn_out)
        x = Dropout(0.2)(x)
        outputs = Dense(1)(x)
        
        model = Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer='adam', loss='mse')
        model.fit(X_train_lstm, y_train_lstm_scaled, epochs=50, verbose=0)
        
        y_pred_scaled = model.predict(X_test_lstm, verbose=0)
        y_pred_ret_test = scaler_y.inverse_transform(y_pred_scaled).flatten()
        y_pred_test = X_test["close"].values * (1 + y_pred_ret_test)
        
        next_ret_scaled = model.predict(latest_row_lstm, verbose=0)
        latest_ret_pred = float(scaler_y.inverse_transform(next_ret_scaled)[0][0])
        next_close_pred = float(latest_row["close"].iloc[0] * (1 + latest_ret_pred))
    else:
        model = Ridge(alpha=1.0)
        model.fit(X_train_scaled, y_train)
        y_pred_ret_test = model.predict(X_test_scaled)
        y_pred_test = X_test["close"].values * (1 + y_pred_ret_test)
        latest_ret_pred = float(model.predict(latest_row_scaled)[0])
        next_close_pred = float(latest_row["close"].iloc[0] * (1 + latest_ret_pred))
        
    y_true_actual_price = X_test["close"].values * (1 + y_test.values)
    mae = float(mean_absolute_error(y_true_actual_price, y_pred_test))
    current_close = float(close.iloc[-1])
    error_pct = float((mae / current_close) * 100) if current_close != 0 else 0.0

    return {
        "predicted_close": next_close_pred,
        "mae": mae,
        "mae_pct_of_price": error_pct,
        "train_rows": float(len(X_train)),
        "test_rows": float(len(X_test)),
        "test_dates": list(X_test.index),
        "y_pred_ret_test": y_pred_ret_test.tolist()
    }


def compare_all_models(
    df: pd.DataFrame,
    lookback: int = 60,
    test_size: float = 0.2,
) -> Optional[Dict[str, Dict]]:
    if not _validate_price_df(df):
        return None
    if lookback < 5 or not (0.05 <= test_size <= 0.5):
        return None

    close = df["close"].astype(float).copy()
    if len(close) < 25:
        return None

    feat, _ = _build_features(df)

    min_required = 18 if len(close) < 60 else 30
    if len(feat) < min_required:
        return None

    X = feat.drop(columns=["target"])
    y = feat["target"]

    split_idx = int(len(feat) * (1 - test_size))
    if split_idx <= 0 or split_idx >= len(feat):
        return None

    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    if X_test.empty:
        return None

    today_close = X_test["close"].values
    y_true_actual = today_close * (1 + y_test.values)

    results = {
        "test_dates": list(X_test.index),
        "y_true": y_true_actual.tolist(),
        "models": {}
    }

    def get_metrics(y_pred_ret):
        y_pred = today_close * (1 + y_pred_ret)
        mae = float(mean_absolute_error(y_true_actual, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_true_actual, y_pred)))
        r2 = float(r2_score(y_true_actual, y_pred))
        
        # Calculate MAPE (handling zero division)
        mape = float(np.mean(np.abs((y_true_actual - y_pred) / np.where(y_true_actual == 0, 1e-8, y_true_actual)))) * 100
        
        actual_dir = (y_true_actual > today_close).astype(int)
        pred_dir = (y_pred > today_close).astype(int)
        acc = float(accuracy_score(actual_dir, pred_dir))
        f1 = float(f1_score(actual_dir, pred_dir, zero_division=0))
        cm = confusion_matrix(actual_dir, pred_dir, labels=[0, 1]).tolist()
        return {"MAE": mae, "RMSE": rmse, "MAPE": mape, "R2": r2, "Direction Accuracy": acc, "F1 Score": f1, "CM": cm, "y_pred": y_pred.tolist()}

    rob_scaler = RobustScaler()
    X_train_scaled = rob_scaler.fit_transform(X_train)
    X_test_scaled = rob_scaler.transform(X_test)

    # 1. Ridge Regression (Replaces Linear Regression)
    lr = Ridge(alpha=1.0)
    lr.fit(X_train_scaled, y_train)
    y_pred_lr_ret = lr.predict(X_test_scaled)
    results["models"]["Linear Regression"] = get_metrics(y_pred_lr_ret)

    # 2. XGBoost
    xg = xgb.XGBRegressor(n_estimators=50, max_depth=3, reg_lambda=1.0, learning_rate=0.1, random_state=42)
    xg.fit(X_train_scaled, y_train)
    y_pred_xg_ret = xg.predict(X_test_scaled)
    results["models"]["XGBoost"] = get_metrics(y_pred_xg_ret)

    # 3. LightGBM
    try:
        import lightgbm as lgb
        lgbm = lgb.LGBMRegressor(n_estimators=50, max_depth=3, learning_rate=0.1, random_state=42)
        lgbm.fit(X_train_scaled, y_train)
        y_pred_lgb_ret = lgbm.predict(X_test_scaled)
        results["models"]["LightGBM"] = get_metrics(y_pred_lgb_ret)
    except Exception as e:
        results["models"]["LightGBM"] = {"error": str(e)}

    # 4. CNN-LSTM
    try:
        import os
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
        import tensorflow as tf
        import random
        random.seed(42)
        np.random.seed(42)
        tf.random.set_seed(42)
        
        from tensorflow.keras.models import Model
        from tensorflow.keras.layers import Input, Conv1D, MaxPooling1D, LSTM, Dense, Dropout, Attention, GlobalAveragePooling1D
        from sklearn.preprocessing import MinMaxScaler
        
        scaler_y = MinMaxScaler()
        y_train_lstm_scaled = scaler_y.fit_transform(y_train.values.reshape(-1, 1))
        
        X_train_lstm = X_train_scaled.reshape((X_train_scaled.shape[0], X_train_scaled.shape[1], 1))
        X_test_lstm = X_test_scaled.reshape((X_test_scaled.shape[0], X_test_scaled.shape[1], 1))
        
        inputs = Input(shape=(X_train_lstm.shape[1], X_train_lstm.shape[2]))
        x = Conv1D(filters=32, kernel_size=2, activation='relu')(inputs)
        x = MaxPooling1D(pool_size=2)(x)
        lstm_out = LSTM(50, activation='relu', return_sequences=True)(x)
        attn_out = Attention()([lstm_out, lstm_out])
        
        x = GlobalAveragePooling1D()(attn_out)
        x = Dropout(0.2)(x)
        outputs = Dense(1)(x)
        
        cnn_lstm_model = Model(inputs=inputs, outputs=outputs)
        cnn_lstm_model.compile(optimizer='adam', loss='mse')
        cnn_lstm_model.fit(X_train_lstm, y_train_lstm_scaled, epochs=50, verbose=0)
        y_pred_scaled = cnn_lstm_model.predict(X_test_lstm, verbose=0)
        y_pred_lstm_ret = scaler_y.inverse_transform(y_pred_scaled).flatten()
        results["models"]["CNN-LSTM"] = get_metrics(y_pred_lstm_ret)
    except Exception as e:
        results["models"]["CNN-LSTM"] = {"error": str(e)}

    return results
