# OpenTrade Analytics — Product Requirements Document

## Objective
A web-based dashboard for NSE stock analysis that provides predictive signals (Buy/Sell), suggests position sizing (how much to buy), and manages a virtual portfolio to track performance.

## Target User
- Retail traders looking for data-driven insights.
- Students/Developers wanting to showcase quantitative finance skills.

## Core Features

### 1. Market Data Explorer
Fetch NSE stock data (OHLCV) with a delay using free sources.

### 2. Technical Analysis Engine
Automated calculation of indicators — RSI, MACD, Moving Averages, etc.

### 3. Predictive Intelligence
- **Signal Generation:** Buy, Sell, or Hold based on technical rules.
- **Price Forecasting:** Predict the next N days' price trend using ML.

### 4. Position Sizing Module
Calculate optimal number of shares to buy based on user-defined "Risk per Trade" percentage.

### 5. Virtual Portfolio Manager
- Add/Remove virtual trades.
- Track real-time P&L of holdings.
- Dashboard showing total portfolio value and sector distribution.

### 6. Backtesting (Lite)
Test a simple strategy against historical data to evaluate performance.

## User Stories
- *"As a trader, I want to enter a stock symbol (e.g., RELIANCE) and see if the current technicals suggest a Buy or Sell."*
- *"As a risk-conscious investor, I want the system to tell me exactly how many shares to buy so I don't lose more than 2% of my capital on one trade."*
- *"As a user, I want to see my current virtual holdings and how much money I have made or lost today."*
