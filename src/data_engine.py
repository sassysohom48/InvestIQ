import yfinance as yf
import pandas as pd
from typing import Optional

NSE_SUFFIX = ".NS"


def _ensure_nse_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol.endswith(NSE_SUFFIX):
        symbol += NSE_SUFFIX
    return symbol


def get_stock_data(
    symbol: str,
    period: str = "3mo",
    interval: str = "1d",
) -> Optional[pd.DataFrame]:
    ticker = _ensure_nse_symbol(symbol)
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
    except Exception:
        return None

    if df is None or df.empty:
        return None

    df.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in df.columns]
    
    if "close" in df.columns:
        df = df.dropna(subset=["close"])
        
    if df.empty:
        return None
        
    df.index = pd.to_datetime(df.index)
    df.index.name = "date"
    return df


def get_current_price(symbol: str) -> Optional[float]:
    ticker = _ensure_nse_symbol(symbol)
    # Prefer download() because it tends to be more stable than Ticker().history()
    # across yfinance versions and cookie/session edge cases.
    try:
        data = yf.download(ticker, period="5d", interval="1d", progress=False)
        if data is not None and not data.empty and "Close" in data.columns:
            close_series = data["Close"]
            if isinstance(close_series, pd.DataFrame):
                close_series = close_series.iloc[:, 0]
            close_series = close_series.dropna()
            if not close_series.empty:
                return float(close_series.iloc[-1])
    except Exception:
        pass

    # Fallback to Ticker fast_info/info when download path fails.
    try:
        stock = yf.Ticker(ticker)
        fast_info = getattr(stock, "fast_info", None)
        if fast_info:
            for key in ("last_price", "regular_market_price"):
                value = fast_info.get(key) if hasattr(fast_info, "get") else None
                if value is not None:
                    return float(value)
        info = getattr(stock, "info", {}) or {}
        value = info.get("regularMarketPrice")
        if value is not None:
            return float(value)
    except Exception:
        return None

    return None
