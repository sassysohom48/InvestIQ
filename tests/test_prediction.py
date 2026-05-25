import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.analysis_engine import predict_price
from src.data_engine import get_stock_data


def test_predict_price_synthetic() -> None:
    np.random.seed(42)
    steps = 220
    trend = np.linspace(100, 180, steps)
    noise = np.random.normal(0, 1.2, steps)
    close = trend + noise
    df = pd.DataFrame({"close": close})

    result = predict_price(df, lookback=60, test_size=0.2)
    assert result is not None, "predict_price should return metrics"
    assert result["predicted_close"] > 0
    assert result["mae"] >= 0
    print(f"  synthetic prediction: {result}")


def test_predict_price_live() -> None:
    df = get_stock_data("RELIANCE", period="6mo")
    assert df is not None and not df.empty, "Failed to fetch RELIANCE data"
    result = predict_price(df, lookback=60, test_size=0.2)
    assert result is not None, "Live prediction should return metrics"
    print(f"  RELIANCE prediction: {result}")


if __name__ == "__main__":
    print("Running prediction tests...\n")
    test_predict_price_synthetic()
    test_predict_price_live()
    print("\nPhase 3 prediction tests passed!")
