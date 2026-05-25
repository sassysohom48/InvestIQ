# OpenTrade Analytics - Project Development Plan

A step-by-step implementation roadmap. Each phase builds on the previous one.

---

## Phase 1 - Project Scaffold & Data Engine

**Goal:** Working directory, dependencies, and ability to fetch NSE stock data.

- [x] Initialize project structure (`src/`, `data/`, `tests/`)
- [x] Create `requirements.txt` (yfinance, pandas, numpy, streamlit, plotly, pandas_ta, scikit-learn)
- [x] Implement `data_engine.py` - `get_stock_data(symbol, period)`
- [x] Write a quick test script to verify data fetch for `RELIANCE.NS`
- [x] Verify `.NS` suffix handling + error handling for invalid symbols

**Deliverable:** `python -c "from src.data_engine import get_stock_data; print(get_stock_data('RELIANCE', '1mo'))"` returns a DataFrame.

**Status (May 25, 2026):** Phase 1 implementation completed in repository files. Runtime verification depends on network access to Yahoo Finance.

---

## Phase 2 - Technical Analysis Engine

**Goal:** Compute indicators and generate Buy/Sell/Hold signals.

- [x] Implement `analysis_engine.py`:
  - `apply_indicators(df)` - RSI(14), MACD, SMA(20/50)
  - `generate_signal(df)` - rule-based: RSI < 30 -> Buy, RSI > 70 -> Sell, else Hold
- [x] Implement `calculate_position_size(capital, risk_pct, stop_loss, current_price)`
- [x] Test on 5 different NSE stocks, log signal output

**Deliverable:** A script that prints signal + position size for any given symbol.

**Status (May 25, 2026):** Implemented in `src/analysis_engine.py` and validated via `tests/test_analysis_engine.py`.

---

## Phase 3 - ML Price Prediction

**Goal:** Forecast tomorrow's closing price using a simple model.

- [x] Implement `predict_price(df)` using scikit-learn Linear Regression
  - Features: last 60 days of close prices, simple moving averages
  - Target: next day's close
- [x] Validate with Mean Absolute Error on a test split
- [ ] (Optional) Add Prophet as an alternative forecaster

**Deliverable:** `predict_price()` returns predicted close and confidence/error metric.

**Status (May 25, 2026):** Implemented in `src/analysis_engine.py` and validated via `tests/test_prediction.py` (synthetic + live RELIANCE data).

---

## Phase 4 - Portfolio Manager (SQLite)

**Goal:** Virtual portfolio CRUD with P&L tracking.

- [x] Design `portfolio_manager.py`:
  - `init_db()` - create tables on first run
  - `add_trade(symbol, qty, buy_price)`
  - `remove_trade(trade_id)`
  - `get_holdings()` - list all open positions
  - `get_portfolio_value()` - current price x qty for each, compute P&L
- [x] Implement `transactions` table for history
- [x] Test: add 3 trades, fetch portfolio value, verify P&L manually

**Deliverable:** A script that can add/remove trades and print portfolio P&L.

**Status (May 25, 2026):** Implemented in `src/portfolio_manager.py` and validated via `tests/test_portfolio_manager.py`.

---

## Phase 5 - Streamlit Dashboard (MVP)

**Goal:** A working web UI with all core features accessible.

- [x] Create `app_ui.py` - Streamlit entry point
- [x] **Sidebar:**
  - Stock symbol input
  - Risk % slider
  - Capital input
- [x] **Main panel:**
  - Candlestick chart (Plotly) from yfinance data
  - Signal card (green BUY / red SELL / yellow HOLD)
  - Predicted price display
  - Position sizing result
- [x] **Portfolio tab:**
  - Table of holdings with live P&L
  - Add/Remove trade forms
  - Total portfolio value

**Deliverable:** Run `streamlit run src/app_ui.py` - fully functional local dashboard.

**Status (May 25, 2026):** MVP implemented in `src/app_ui.py` and integrated with data, analysis, prediction, risk sizing, and portfolio modules.

---

## Phase 6 - Backtesting Lite

**Goal:** Test a simple moving-average crossover strategy.

- [x] Implement `backtest.py`:
  - SMA crossover strategy (e.g., buy when SMA20 crosses above SMA50)
  - Compute total return, win rate, max drawdown
  - Plot equity curve
- [x] Run on 5 stocks over 2 years, print performance summary

**Deliverable:** Backtest results visible from the dashboard UI.

**Status (May 25, 2026):** Implemented in `src/backtest.py`, integrated into `src/app_ui.py` Backtest tab, and validated via `tests/test_backtest.py`.

---

## Phase 7 - Polish & Deploy

**Goal:** Deploy to Streamlit Cloud for public access.

- [x] Add `requirements.txt` at root
- [x] Add `streamlit` config (`config.toml` if needed)
- [ ] Push to GitHub public repo
- [ ] Deploy via Streamlit Cloud (connect GitHub repo)
- [x] Add README.md with demo instructions

**Deliverable:** Live URL (e.g., `https://opentrade-analytics.streamlit.app`).

**Status (May 25, 2026):** Deployment prep completed (`README.md`, `.streamlit/config.toml`, root `requirements.txt`). Remaining: push repo and deploy on Streamlit Cloud.

---

## Future Enhancements (Post-MVP)

- [ ] Multi-user authentication (Streamlit secrets / session state)
- [ ] Real-time WebSocket data (if a free source emerges)
- [ ] More ML models (LSTM, XGBoost)
- [ ] Export portfolio to CSV
- [ ] Sector-wise allocation pie chart
- [ ] Email/SMS alerts on signal triggers
