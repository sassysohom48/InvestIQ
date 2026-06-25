import sys
import os
import traceback

sys.path.append(os.path.abspath('c:/Users/sohom/OneDrive/Desktop/InvestIQ'))

NIFTY_50_SYMBOLS = {
    "RELIANCE": "Reliance Industries Limited",
    "TCS": "Tata Consultancy Services Limited",
    "HDFCBANK": "HDFC Bank Limited",
    "ICICIBANK": "ICICI Bank Limited",
    "INFY": "Infosys Limited",
    "ITC": "ITC Limited",
    "SBIN": "State Bank of India",
    "BHARTIARTL": "Bharti Airtel Limited",
    "HINDUNILVR": "Hindustan Unilever Limited",
    "LARSEN": "Larsen & Toubro Limited",
    "WIPRO": "Wipro Limited",
    "HCLTECH": "HCL Technologies Limited",
    "BAJFINANCE": "Bajaj Finance Limited",
    "AXISBANK": "Axis Bank Limited",
    "MARUTI": "Maruti Suzuki India Limited",
    "SUNPHARMA": "Sun Pharmaceutical Industries Limited",
    "ULTRACEMCO": "UltraTech Cement Limited",
    "TITAN": "Titan Company Limited",
    "ASIANPAINT": "Asian Paints Limited",
    "M&M": "Mahindra & Mahindra Limited",
    "NTPC": "NTPC Limited",
    "POWERGRID": "Power Grid Corporation of India Limited",
    "KOTAKBANK": "Kotak Mahindra Bank Limited",
    "TATASTEEL": "Tata Steel Limited",
    "BAJAJFINSV": "Bajaj Finserv Limited",
    "INDUSINDBK": "IndusInd Bank Limited",
    "NESTLEIND": "Nestle India Limited",
    "TECHM": "Tech Mahindra Limited",
    "GRASIM": "Grasim Industries Limited",
    "JSWSTEEL": "JSW Steel Limited",
    "HINDALCO": "Hindalco Industries Limited",
    "ADANIPORTS": "Adani Ports and Special Economic Zone Limited",
    "ONGC": "Oil and Natural Gas Corporation Limited",
    "COALINDIA": "Coal India Limited",
    "CIPLA": "Cipla Limited",
    "TATAMOTORS": "Tata Motors Limited",
    "BRITANNIA": "Britannia Industries Limited",
    "APOLLOHOSP": "Apollo Hospitals Enterprise Limited",
    "HEROMOTOCO": "Hero MotoCorp Limited",
    "EICHERMOT": "Eicher Motors Limited",
    "DIVISLAB": "Divi's Laboratories Limited",
    "UPL": "UPL Limited",
    "DRREDDY": "Dr. Reddy's Laboratories Limited",
    "HDFCLIFE": "HDFC Life Insurance Company Limited",
    "SBILIFE": "SBI Life Insurance Company Limited",
    "BPCL": "Bharat Petroleum Corporation Limited",
}

try:
    from src.data_engine import get_stock_data
    from src.analysis_engine import apply_indicators, generate_signal

    print("Checking signals for Nifty 50 companies...")
    for symbol in NIFTY_50_SYMBOLS.keys():
        try:
            df = get_stock_data(symbol, "1y")
            df_enc = apply_indicators(df)
            sig = generate_signal(df_enc)
            if sig != "HOLD":
                print(f"--> {symbol}: {sig}")
        except Exception as e:
            pass
    print("Done checking.")
except Exception as e:
    traceback.print_exc()
