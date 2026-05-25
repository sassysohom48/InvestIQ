import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_engine import get_stock_data, get_current_price, _ensure_nse_symbol


def test_ensure_nse_symbol():
    assert _ensure_nse_symbol("RELIANCE") == "RELIANCE.NS"
    assert _ensure_nse_symbol("reliance") == "RELIANCE.NS"
    assert _ensure_nse_symbol("RELIANCE.NS") == "RELIANCE.NS"
    assert _ensure_nse_symbol("tcs.NS") == "TCS.NS"
    print("  _ensure_nse_symbol: OK")


def test_get_stock_data():
    df = get_stock_data("RELIANCE", period="1mo")
    assert df is not None, "DataFrame should not be None"
    assert not df.empty, "DataFrame should not be empty"
    required_cols = {"open", "high", "low", "close", "volume"}
    assert required_cols.issubset(set(df.columns)), f"Missing columns. Got: {list(df.columns)}"
    assert df.index.name == "date", f"Index name should be 'date', got '{df.index.name}'"
    print(f"  Columns: {list(df.columns)}")
    print(f"  Rows: {len(df)}")
    print(f"  Date range: {df.index[0]} to {df.index[-1]}")
    print("  get_stock_data: OK")


def test_invalid_symbol():
    df = get_stock_data("INVALID12345", period="1mo")
    assert df is None, "Invalid symbol should return None"
    print("  invalid symbol -> None: OK")


def test_get_current_price():
    price = get_current_price("RELIANCE")
    assert price is not None, "Price should not be None"
    assert isinstance(price, float), "Price should be float"
    assert price > 0, f"Price should be positive, got {price}"
    print(f"  RELIANCE current price: {price}")
    print("  get_current_price: OK")


if __name__ == "__main__":
    print("Running data_engine tests...\n")
    test_ensure_nse_symbol()
    test_get_stock_data()
    test_invalid_symbol()
    test_get_current_price()
    print("\nAll tests passed!")
