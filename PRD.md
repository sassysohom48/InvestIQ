# InvestIQ — Product Requirements Document

## Objective
A web-based dashboard for NSE stock analysis that provides predictive signals (Buy/Sell), bulk sector scanning, suggests position sizing (how much to buy), performs sentiment analysis, and manages a virtual portfolio with multi-user support to track performance.

## Target User
- Retail traders looking for data-driven insights and AI models.
- Quantitative analysts wanting to backtest strategies.
- Portfolio managers looking to track sector-wise allocations.

## Core Features

### 1. Market Data Explorer
Fetch NSE stock data (OHLCV) dynamically with interactive candlestick charts and historical analysis.

### 2. Technical Analysis Engine
Automated calculation of indicators — RSI, MACD, Moving Averages, Bollinger Bands.

### 3. Predictive Intelligence & AI
- **Signal Generation:** Actionable Buy, Sell, or Hold signals based on technical crossover rules.
- **Price Forecasting:** Predict the next N days' price trend using Linear Regression, XGBoost, and LSTM models side-by-side.
- **Sentiment Analysis:** Live news headline aggregation and NLP sentiment scoring via VADER (Bullish/Bearish).

### 4. Trade Screener
A bulk scanner that instantly analyzes major Nifty indices (Nifty 50, Bank, IT, Auto, Pharma, etc.) and lists all stocks with actionable BUY or SELL signals.

### 5. Position Sizing & Optimization
- Calculate the optimal number of shares to buy based on user-defined "Risk per Trade" percentage and 2x ATR dynamic stop loss.
- **Portfolio Optimizer:** Markowitz Efficient Frontier to suggest the optimal weighting of stocks in a portfolio to maximize the Sharpe ratio.

### 6. Virtual Portfolio Manager
- Multi-user authentication (Registration, Login, Password Reset).
- Admin dashboard to monitor global system usage.
- Add/Remove virtual trades, track real-time P&L, sector distribution pie charts, and CSV exports.

### 7. Backtesting & Strategy Builder
Test Simple Moving Average crossovers and custom strategies against historical data, plotting the resulting equity curve.

### 8. Alerting System
Automated SMTP-based email alerts to notify users of actionable trade setups.

## User Stories
- *"As a trader, I want to scan the entire Nifty IT basket to see if there are any immediate Buy signals."*
- *"As a risk-conscious investor, I want the system to tell me exactly how many shares to buy so I don't lose more than 2% of my capital."*
- *"As a user, I want to see my current virtual holdings and export my P&L to a spreadsheet."*
- *"As an analyst, I want to see what live news is saying about a stock and whether the sentiment is Bullish or Bearish."*
