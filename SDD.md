# InvestIQ — Software Design Document

## System Architecture (Modular Monolith)

```
        User Interface (Streamlit app_ui.py)
                         |
      ----------------------------------------
      |                  |                   |
 Data Engine      Analysis Engine      Portfolio Manager
      |                  |                   |
 Yahoo Finance    ML Models (LSTM,     SQLite (Multi-user)
                  XGBoost) + VADER
```

## Module Breakdown

### 1. `data_engine.py`
- Fetches historical OHLCV data via `yfinance`.
- Appends `.NS` suffix for NSE symbols.

### 2. `analysis_engine.py`
- **`apply_indicators(df)`** — Adds RSI, MACD, Moving Averages, Bollinger Bands.
- **`generate_signal(df)`** — Rules-based signal (Buy/Sell/Hold) based on MACD/RSI crossovers.
- **`predict_price()`** — Forecasts next close using Linear Regression, XGBoost, or LSTM models.
- **`compare_all_models()`** — Runs all models and returns metrics (MAE).
- **`calculate_position_size()`** — Math for 2x ATR dynamic stop loss and risk-based sizing.

### 3. `sentiment_engine.py`
- Fetches live news headlines via DuckDuckGo/News APIs.
- Uses VADER Sentiment Analysis to score headlines as Bullish, Bearish, or Neutral.

### 4. `portfolio_manager.py`
- Multi-user authentication (password hashing, sessions).
- CRUD operations for SQLite `holdings`, `transactions`, and `users` tables.
- Calculates P&L and Sector Allocation distribution.

### 5. `portfolio_optimizer.py`
- **`optimize_portfolio()`** — Calculates the Markowitz Efficient Frontier to maximize Sharpe ratio based on historical covariance matrices.

### 6. `app_ui.py` (Streamlit entry point)
- **Routing:** Tab-based UI layout.
- **Admin Panel:** Global user monitoring.
- **Market View:** Candlesticks, signal cards, sentiment breakdown.
- **Trade Screener:** Bulk-scanning Nifty indices for signals.
- **Portfolio:** Interactive tables, add/remove trades, pie charts, CSV exports.
- **Backtest / Strategy Builder:** SMA strategy testing and visualization.

## Database Schema (SQLite)

### Table: `users`
| Column | Type | Description |
| :--- | :--- | :--- |
| id | INTEGER | PK |
| username | TEXT | Unique username |
| email | TEXT | Unique email |
| password_hash | TEXT | Bcrypt hash |
| role | TEXT | 'admin' or 'user' |

### Table: `holdings`
| Column | Type | Description |
| :--- | :--- | :--- |
| id | INTEGER | PK |
| user_id | INTEGER | FK to users.id |
| symbol | TEXT | Stock symbol |
| quantity | INTEGER | Shares held |
| avg_price | REAL | Entry price |

### Table: `transactions`
| Column | Type | Description |
| :--- | :--- | :--- |
| id | INTEGER | PK |
| user_id | INTEGER | FK to users.id |
| type | TEXT | BUY/SELL |
| symbol | TEXT | Stock symbol |
| price | REAL | Exec price |
| quantity | INTEGER | Shares |
| timestamp | TEXT | Timestamp |
