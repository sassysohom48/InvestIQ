import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_engine import get_stock_data


def main() -> int:
    symbol = "RELIANCE.NS"
    df = get_stock_data(symbol, period="1mo")
    if df is None or df.empty:
        print("FAILED: Could not fetch data for RELIANCE.NS")
        return 1

    print(f"SUCCESS: fetched {len(df)} rows for {symbol}")
    print(df.tail(3))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
