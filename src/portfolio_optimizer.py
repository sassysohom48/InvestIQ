import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize

def optimize_portfolio(symbols: list, risk_free_rate: float = 0.07) -> dict:
    """
    Given a list of stock symbols, downloads historical data and uses
    Modern Portfolio Theory to find the weights that maximize the Sharpe Ratio.
    Returns:
        {
            "optimal_weights": {symbol: weight_pct},
            "expected_return": float,
            "expected_volatility": float,
            "sharpe_ratio": float,
            "error": str (if any)
        }
    """
    if not symbols or len(symbols) < 2:
        return {"error": "Portfolio must contain at least 2 distinct stocks for optimization."}
        
    tickers = []
    for s in symbols:
        tickers.append(s if s.endswith(".NS") else f"{s}.NS")
        
    # Download 1 year of data
    try:
        data = yf.download(tickers, period="1y", group_by="ticker", progress=False)
    except Exception as e:
        return {"error": f"Failed to download market data: {str(e)}"}
        
    if data.empty:
        return {"error": "No market data found for the given symbols."}
        
    # Extract adjusted close prices (or close if adj close is missing)
    price_df = pd.DataFrame()
    for s, t in zip(symbols, tickers):
        if len(tickers) == 1:
            df_ticker = data
        else:
            if t in data.columns.levels[0]:
                df_ticker = data[t]
            else:
                continue
                
        if "Adj Close" in df_ticker.columns:
            price_df[s] = df_ticker["Adj Close"]
        elif "Close" in df_ticker.columns:
            price_df[s] = df_ticker["Close"]
            
    if price_df.empty or price_df.shape[1] < 2:
        return {"error": "Insufficient valid price data for optimization."}
        
    # Forward fill missing data
    price_df.ffill(inplace=True)
    price_df.dropna(inplace=True)
    
    # Calculate daily log returns
    returns = np.log(price_df / price_df.shift(1)).dropna()
    
    # Annualized return and covariance
    trading_days = 252
    mean_returns = returns.mean() * trading_days
    cov_matrix = returns.cov() * trading_days
    
    num_assets = len(price_df.columns)
    symbols_used = list(price_df.columns)
    
    def portfolio_performance(weights, mean_returns, cov_matrix):
        returns_p = np.sum(mean_returns * weights)
        std_p = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return returns_p, std_p
        
    def negative_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate):
        p_ret, p_std = portfolio_performance(weights, mean_returns, cov_matrix)
        return -(p_ret - risk_free_rate) / p_std
        
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0.0, 1.0) for asset in range(num_assets))
    init_guess = num_assets * [1. / num_assets,]
    
    optimized = minimize(
        negative_sharpe_ratio, 
        init_guess, 
        args=(mean_returns, cov_matrix, risk_free_rate), 
        method='SLSQP', 
        bounds=bounds, 
        constraints=constraints
    )
    
    if not optimized.success:
        return {"error": f"Optimization failed: {optimized.message}"}
        
    opt_weights = optimized.x
    exp_ret, exp_std = portfolio_performance(opt_weights, mean_returns, cov_matrix)
    opt_sharpe = (exp_ret - risk_free_rate) / exp_std
    
    weight_dict = {sym: float(w * 100) for sym, w in zip(symbols_used, opt_weights)}
    
    return {
        "optimal_weights": weight_dict,
        "expected_return": float(exp_ret * 100),
        "expected_volatility": float(exp_std * 100),
        "sharpe_ratio": float(opt_sharpe),
        "error": None
    }
