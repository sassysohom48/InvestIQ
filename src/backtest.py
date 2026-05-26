from __future__ import annotations

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


def run_sma_crossover_backtest(
    df: pd.DataFrame,
    short_window: int = 20,
    long_window: int = 50,
    drop_incomplete_last_candle: bool = True,
) -> Optional[Dict[str, object]]:
    if not isinstance(df, pd.DataFrame) or df.empty or "close" not in df.columns:
        return None
    if short_window <= 0 or long_window <= 0 or short_window >= long_window:
        return None

    data = df.copy()
    data["close"] = data["close"].astype(float)

    # During market hours, today's daily candle may still be in-progress.
    # For backtesting, exclude the partial last bar to keep stats based on completed sessions.
    if drop_incomplete_last_candle and len(data) >= 2 and _is_nse_open_now():
        try:
            last_idx_date = pd.Timestamp(data.index[-1]).date()
            now_ist_date = datetime.now(ZoneInfo("Asia/Kolkata")).date()
            if last_idx_date == now_ist_date:
                data = data.iloc[:-1].copy()
        except Exception:
            pass

    data["sma_short"] = data["close"].rolling(short_window).mean()
    data["sma_long"] = data["close"].rolling(long_window).mean()
    data = data.dropna().copy()
    if data.empty:
        return None

    data["signal"] = (data["sma_short"] > data["sma_long"]).astype(int)
    data["position_change"] = data["signal"].diff().fillna(0)

    data["asset_returns"] = data["close"].pct_change().fillna(0.0)
    data["strategy_returns"] = data["asset_returns"] * data["signal"].shift(1).fillna(0)
    data["equity_curve"] = (1 + data["strategy_returns"]).cumprod()

    total_return = float((data["equity_curve"].iloc[-1] - 1) * 100.0)

    trades = data.loc[data["position_change"] != 0, ["position_change", "strategy_returns"]].copy()
    closed_trade_returns = trades.loc[trades["position_change"] == -1, "strategy_returns"]
    wins = int((closed_trade_returns > 0).sum())
    total_closed = int(len(closed_trade_returns))
    win_rate = float((wins / total_closed) * 100.0) if total_closed > 0 else 0.0

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
                "sma_short",
                "sma_long",
                "signal",
                "asset_returns",
                "strategy_returns",
                "equity_curve",
            ]
        ].copy(),
    }
