# InvestIQ - Project Development Plan

A step-by-step implementation roadmap showing the project's evolution.

---

## Phase 1 - Project Scaffold & Data Engine

- `[x]` Initialize project structure (`src/`, `data/`, `tests/`)
- `[x]` Create `requirements.txt`
- `[x]` Implement `data_engine.py` - `get_stock_data(symbol, period)`
- `[x]` Handle `.NS` suffix handling + error handling for invalid symbols

---

## Phase 2 - Technical Analysis Engine

- `[x]` Implement `analysis_engine.py`:
  - `[x]` Indicators: RSI(14), MACD, SMA(20/50), Bollinger Bands
  - `[x]` Signals: Rule-based generation (RSI/MACD crossovers)
- `[x]` Implement `calculate_position_size(capital, risk_pct, stop_loss, current_price)`

---

## Phase 3 - ML Price Prediction & Advanced Analytics

- `[x]` Implement `predict_price(df)` using scikit-learn Linear Regression
- `[x]` Implement LSTM Time-Series forecasting model
- `[x]` Implement XGBoost Gradient Boosting model
- `[x]` Implement `compare_all_models()` for side-by-side performance evaluation (MAE)
- `[x]` Integrate Live News Sentiment Analysis via VADER (Bullish/Bearish NLP scoring)
- `[x]` Implement `optimize_portfolio()` using Markowitz Efficient Frontier

---

## Phase 4 - Advanced Portfolio Manager (SQLite)

- `[x]` Design `portfolio_manager.py` with multi-user support
- `[x]` Implement user authentication (Registration, Login, Password Reset)
- `[x]` Admin panel for managing users and monitoring global portfolios
- `[x]` Track holdings, P&L, transaction history
- `[x]` Sector-wise allocation pie charts and portfolio CSV exports

---

## Phase 5 - Streamlit Dashboard (UI/UX)

- `[x]` Create `app_ui.py` - Advanced Streamlit entry point
- `[x]` **Market View:** Candlestick charts, signal cards, ML predictions
- `[x]` **Trade Screener:** Bulk-scan Nifty 50, Nifty Bank, Nifty IT, Auto, Pharma, FMCG, Metal, etc.
- `[x]` **Backtest & Strategy Builder:** Custom parameter testing and equity curve plotting
- `[x]` **Custom Theme Engine:** Native CSS overrides for premium UI/UX, floating cards, hover micro-animations

---

## Phase 6 - Alerting & Polish

- `[x]` Integrate SMTP Email Alerting for active trade signals
- `[x]` Add comprehensive Error Handling and Fallbacks
- `[x]` Streamline and Refactor `app_ui.py` to handle complex routing

---

## Phase 7 - Deployment

- `[x]` Ensure `requirements.txt` is updated
- `[x]` Update Documentation (README, PDP, PRD, SDD)
- `[x]` Push to GitHub public repo
- `[x]` Deploy via Streamlit Community Cloud

**Status (June 2026):** All Phases Complete. Project ready for production deployment.
