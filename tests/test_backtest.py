import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.backtest import run_sma_crossover_backtest
from src.data_engine import get_stock_data


def test_backtest_on_5_stocks() -> None:
    symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ITC"]
    print("Running SMA crossover backtest on 5 stocks (2y)...")
    for symbol in symbols:
        df = get_stock_data(symbol, period="2y")
        assert df is not None and not df.empty, f"Failed to fetch data for {symbol}"
        result = run_sma_crossover_backtest(df, short_window=20, long_window=50)
        assert result is not None, f"Backtest failed for {symbol}"
        summary = result["summary"]
        print(
            f"  {symbol}.NS -> return={summary['total_return_pct']:.2f}% | "
            f"win_rate={summary['win_rate_pct']:.2f}% | "
            f"max_drawdown={summary['max_drawdown_pct']:.2f}%"
        )


if __name__ == "__main__":
    test_backtest_on_5_stocks()
    print("\nPhase 6 backtesting tests passed!")
