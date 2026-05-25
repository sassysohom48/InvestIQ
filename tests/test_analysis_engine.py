import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.analysis_engine import apply_indicators, calculate_position_size, generate_signal
from src.data_engine import get_stock_data


def test_apply_indicators_and_signal() -> None:
    close_values = list(range(100, 180))
    df = pd.DataFrame({"close": close_values})
    out = apply_indicators(df)
    assert out is not None, "apply_indicators should return DataFrame"

    expected_cols = {"sma_20", "sma_50", "rsi_14", "macd", "macd_signal", "macd_hist"}
    assert expected_cols.issubset(set(out.columns)), f"Missing columns: {expected_cols - set(out.columns)}"

    signal = generate_signal(out)
    assert signal in {"BUY", "SELL", "HOLD"}, f"Unexpected signal: {signal}"
    print(f"  indicator columns added: OK")
    print(f"  generated signal: {signal}")


def test_signal_rule_boundaries() -> None:
    buy_df = pd.DataFrame({"rsi_14": [25.0]})
    sell_df = pd.DataFrame({"rsi_14": [75.0]})
    hold_df = pd.DataFrame({"rsi_14": [50.0]})
    assert generate_signal(buy_df) == "BUY"
    assert generate_signal(sell_df) == "SELL"
    assert generate_signal(hold_df) == "HOLD"
    print("  signal boundaries: OK")


def test_position_size() -> None:
    result = calculate_position_size(
        capital=100000,
        risk_pct=2.0,
        stop_loss=1450.0,
        current_price=1500.0,
    )
    assert result["shares"] == 40.0, f"Expected 40 shares, got {result['shares']}"
    assert result["risk_amount"] == 2000.0
    assert result["position_value"] == 60000.0
    print(f"  position sizing: {result}")


def smoke_test_5_nse_stocks() -> None:
    symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ITC"]
    print("  live smoke test on 5 NSE stocks:")
    for symbol in symbols:
        df = get_stock_data(symbol, period="3mo")
        assert df is not None and not df.empty, f"Failed to fetch data for {symbol}"
        out = apply_indicators(df)
        assert out is not None, f"Failed indicators for {symbol}"
        signal = generate_signal(out)
        print(f"    {symbol}.NS -> {signal}")


if __name__ == "__main__":
    print("Running analysis_engine tests...\n")
    test_apply_indicators_and_signal()
    test_signal_rule_boundaries()
    test_position_size()
    smoke_test_5_nse_stocks()
    print("\nAll Phase 2 tests passed!")
