from __future__ import annotations
# Force module reload
from datetime import datetime
from typing import Dict, Optional

import pandas as pd
from zoneinfo import ZoneInfo


def _is_nse_open_now() -> bool:
    now_ist = datetime.now(ZoneInfo("Asia/Kolkata"))
    if now_ist.weekday() >= 5:
        return False
    hhmm = now_ist.hour * 60 + now_ist.minute
    market_open = 9 * 60 + 15
    market_close = 15 * 60 + 30
    return market_open <= hhmm <= market_close


def run_ml_backtest_v2(
    df: pd.DataFrame,
    test_dates: list,
    y_pred_ret_test: list,
    drop_incomplete_last_candle: bool = True,
) -> Optional[Dict[str, object]]:
    if not isinstance(df, pd.DataFrame) or df.empty or "close" not in df.columns:
        return None
    if not test_dates or not y_pred_ret_test or len(test_dates) != len(y_pred_ret_test):
        return None

    data = df.loc[test_dates].copy()
    data["close"] = data["close"].astype(float)

    if drop_incomplete_last_candle and len(data) >= 2 and _is_nse_open_now():
        try:
            last_idx_date = pd.Timestamp(data.index[-1]).date()
            now_ist_date = datetime.now(ZoneInfo("Asia/Kolkata")).date()
            if last_idx_date == now_ist_date:
                data = data.iloc[:-1].copy()
                y_pred_ret_test = y_pred_ret_test[:-1]
        except Exception:
            pass

    data["pred_ret"] = y_pred_ret_test
    data["signal"] = (data["pred_ret"] > 0).astype(int)
    data["position_change"] = data["signal"].diff().fillna(0)

    data["asset_returns"] = data["close"].pct_change().shift(-1).fillna(0.0)
    data["strategy_returns"] = data["asset_returns"] * data["signal"]
    
    # Drop the last row since actual return is unknown
    data = data.iloc[:-1].copy()
    if data.empty:
        return None

    data["equity_curve"] = (1 + data["strategy_returns"]).cumprod()

    total_return = float((data["equity_curve"].iloc[-1] - 1) * 100.0)

    invested_days = data[data["signal"] == 1]
    wins = int((invested_days["strategy_returns"] > 0).sum())
    total_invested = len(invested_days)
    win_rate = float((wins / total_invested) * 100.0) if total_invested > 0 else 0.0
    
    total_closed = int((data["position_change"] == -1).sum())

    running_max = data["equity_curve"].cummax()
    drawdown = (data["equity_curve"] / running_max) - 1.0
    max_drawdown = float(drawdown.min() * 100.0)

    return {
        "summary": {
            "total_return_pct": total_return,
            "win_rate_pct": win_rate,
            "max_drawdown_pct": max_drawdown,
            "num_closed_trades": total_closed,
        },
        "equity_curve": data[["equity_curve"]].copy(),
        "backtest_frame": data[
            [
                "close",
                "pred_ret",
                "signal",
                "asset_returns",
                "strategy_returns",
                "equity_curve",
            ]
        ].copy(),
    }

def run_custom_strategy(df: pd.DataFrame, metric: str, operator: str, threshold: float) -> Optional[Dict[str, object]]:
    """
    Evaluates a custom strategy based on a single condition (e.g., RSI < 30).
    Returns a dictionary with summary stats and the backtest dataframe.
    """
    if df is None or df.empty or metric not in df.columns:
        return None
        
    data = df.copy()
    
    # Generate Buy Signals
    if operator == ">":
        data["signal"] = (data[metric] > threshold).astype(int)
    elif operator == "<":
        data["signal"] = (data[metric] < threshold).astype(int)
    elif operator == ">=":
        data["signal"] = (data[metric] >= threshold).astype(int)
    elif operator == "<=":
        data["signal"] = (data[metric] <= threshold).astype(int)
    elif operator == "==":
        data["signal"] = (data[metric] == threshold).astype(int)
    else:
        return None
        
    data["position_change"] = data["signal"].diff().fillna(0)
    data["asset_returns"] = data["close"].pct_change().shift(-1).fillna(0.0)
    data["strategy_returns"] = data["asset_returns"] * data["signal"]
    
    # Drop the last row since actual return is unknown
    data = data.iloc[:-1].copy()
    if data.empty:
        return None

    data["equity_curve"] = (1 + data["strategy_returns"]).cumprod()

    total_return = float((data["equity_curve"].iloc[-1] - 1) * 100.0)

    invested_days = data[data["signal"] == 1]
    wins = int((invested_days["strategy_returns"] > 0).sum())
    total_invested = len(invested_days)
    win_rate = float((wins / total_invested) * 100.0) if total_invested > 0 else 0.0
    
    total_closed = int((data["position_change"] == -1).sum())

    running_max = data["equity_curve"].cummax()
    drawdown = (data["equity_curve"] / running_max) - 1.0
    max_drawdown = float(drawdown.min() * 100.0)

    return {
        "summary": {
            "total_return_pct": total_return,
            "win_rate_pct": win_rate,
            "max_drawdown_pct": max_drawdown,
            "num_closed_trades": total_closed,
        },
        "equity_curve": data[["equity_curve"]].copy(),
        "backtest_frame": data.copy(),
    }
