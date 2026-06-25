# InvestIQ

InvestIQ is a powerful, NSE-focused stock analysis, machine learning prediction, and virtual portfolio dashboard built with Python and Streamlit.

## 🚀 Features

- **NSE Market View:** Fetch live/historical data with automatic `.NS` symbol handling for Indian stocks.
- **AI/ML Price Prediction:** Compare linear regression, XGBoost, and LSTM models side-by-side to forecast tomorrow's close price.
- **Trade Screener:** Bulk-scan Nifty 50, Nifty Bank, Nifty IT, and other major sectoral indices for instant, actionable BUY/SELL signals.
- **Technical Analysis:** RSI(14), MACD, SMA(20/50), Bollinger Bands.
- **Risk Management:** Dynamic position sizing based on risk percentage and automated 2x ATR stop-loss calculation.
- **Live Sentiment Engine:** Fetches live news headlines and analyzes NLP sentiment (Bullish/Bearish) using VADER.
- **Portfolio Manager:** Virtual portfolio with multi-user authentication, P&L tracking, sector allocation charts, and CSV export.
- **Backtesting & Strategy Builder:** Test SMA crossover and custom technical strategies with equity curves and performance metrics.
- **Custom Theme Engine:** Beautiful, modern UI with floating metrics cards and smooth hover animations.

## 📁 Project Structure

- `src/app_ui.py` - Main Streamlit dashboard application.
- `src/data_engine.py` - Data fetching (yfinance).
- `src/analysis_engine.py` - Indicators, signals, ML predictions.
- `src/portfolio_manager.py` - SQLite multi-user portfolio CRUD + analytics.
- `src/portfolio_optimizer.py` - Markowitz Efficient Frontier optimization.
- `src/backtest.py` - Vectorized backtest engines.
- `src/sentiment_engine.py` - Live news fetching and NLP analysis.
- `src/theme_engine.py` - Custom CSS styling for the UI.
- `src/alerts.py` - Email alert system.

## 💻 Local Setup

1. Create and activate a Python 3.12 environment.
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the app:
```bash
streamlit run src/app_ui.py
```

## ☁️ Deploy to Streamlit Cloud

1. Fork or push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and connect your GitHub account.
3. Deploy `src/app_ui.py`.
4. Add your `.streamlit/secrets.toml` to the Advanced Settings for email alerts to work.

## ⚠️ Disclaimer

- Data is fetched via Yahoo Finance and may be delayed.
- Predictions and backtest results are strictly educational and **do not constitute financial advice**.
