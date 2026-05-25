# OpenTrade Analytics

OpenTrade Analytics is an NSE-focused stock analysis and virtual portfolio dashboard built with Python and Streamlit.

## Features

- NSE data fetch with automatic `.NS` symbol handling
- Technical indicators: RSI(14), MACD, SMA(20/50)
- Rule-based signal generation: BUY / SELL / HOLD
- ML next-day close prediction (Linear Regression + MAE)
- Position sizing based on risk % and stop-loss
- SQLite virtual portfolio manager (add/remove holdings + transaction history)
- SMA crossover backtesting with equity curve and performance metrics

## Project Structure

- `src/data_engine.py` - data fetching and current price lookup
- `src/analysis_engine.py` - indicators, signals, risk sizing, prediction
- `src/portfolio_manager.py` - SQLite portfolio CRUD + P&L
- `src/backtest.py` - SMA crossover backtest engine
- `src/app_ui.py` - Streamlit dashboard
- `tests/` - phase-wise validation scripts

## Local Setup

1. Create/activate a Python environment (recommended Python 3.11+).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run src/app_ui.py
```

## Validation Scripts

```bash
python tests/test_data_engine.py
python tests/test_analysis_engine.py
python tests/test_prediction.py
python tests/test_portfolio_manager.py
python tests/test_backtest.py
```

## Deploy to Streamlit Cloud

1. Push this project to a GitHub repository.
2. Go to Streamlit Community Cloud and create a new app.
3. Select repository and branch.
4. Set main file path to `src/app_ui.py`.
5. Deploy.

## Notes

- Data source: Yahoo Finance via `yfinance`.
- Symbols are normalized to NSE format by appending `.NS` when needed.
- Backtest is educational and not financial advice.
