# OpenTrade Analytics — Software Design Document

## System Architecture (Modular Monolith)

```
User Interface (Streamlit)
        |
   Orchestrator / Main App
       |          |            |
  Data Engine  Analysis    Portfolio
               Engine      Manager
       |          |            |
  Yahoo Finance   ML Models   SQLite
```

## Module Breakdown

### 1. `data_engine.py`
- **`get_stock_data(symbol, period)`**
- Appends `.NS` suffix for NSE symbols.
- Fetches historical OHLCV data via yfinance.
- Returns a cleaned Pandas DataFrame.

### 2. `analysis_engine.py`
- **`apply_indicators(df)`** — Adds RSI, MACD, Moving Averages to DataFrame.
- **`generate_signal(df)`** — Buy if RSI < 30, Sell if RSI > 70, else Hold.
- **`predict_price(df)`** — Trains a Linear Regression or Prophet model on last 60 days to forecast next close.
- **`calculate_position_size(capital, risk_pct, stop_loss_price, current_price)`** — Position sizing math.

### 3. `portfolio_manager.py`
- **`add_trade(symbol, qty, buy_price)`** — SQL INSERT into holdings.
- **`remove_trade(trade_id)`** — SQL DELETE / mark as sold.
- **`get_portfolio_value()`** — SELECT all holdings → fetch current price → calculate P&L.

### 4. `app_ui.py` (Streamlit entry point)
- **Sidebar:** Stock symbol input, risk % slider, portfolio view toggle.
- **Main Panel:** Candlestick charts (Plotly), signal cards (Buy/Sell/Hold), prediction graphs, portfolio table.

## Database Schema (SQLite)

### Table: `holdings`

| Column      | Type    | Description              |
| :---------- | :------ | :----------------------- |
| id          | INTEGER | Primary key (auto)       |
| symbol      | TEXT    | e.g. 'TATASTEEL.NS'      |
| quantity    | INTEGER | Number of shares         |
| avg_price   | REAL    | Average buy price        |
| entry_date  | TEXT    | Date of purchase         |

### Table: `transactions`

| Column      | Type    | Description              |
| :---------- | :------ | :----------------------- |
| id          | INTEGER | Primary key (auto)       |
| type        | TEXT    | 'BUY' or 'SELL'          |
| symbol      | TEXT    | Stock symbol             |
| price       | REAL    | Execution price          |
| quantity    | INTEGER | Shares traded            |
| timestamp   | TEXT    | Time of transaction      |

## Data Flow
1. User enters a symbol in Streamlit UI.
2. `data_engine` fetches data from Yahoo Finance.
3. `analysis_engine` computes indicators, signal, and price prediction.
4. Results rendered as charts and cards in the UI.
5. Portfolio actions (buy/sell) go through `portfolio_manager` to SQLite.
