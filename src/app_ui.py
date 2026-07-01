from __future__ import annotations
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Force hot-reload trigger

import random
from datetime import datetime
from io import StringIO

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import streamlit as st
from zoneinfo import ZoneInfo

from src.analysis_engine import (
    apply_indicators,
    calculate_position_size,
    generate_signal,
    predict_price,
    compare_all_models,
)
from src.backtest import run_ml_backtest_v2, run_custom_strategy
from src.data_engine import get_stock_data
from src.portfolio_manager import (
    init_db,
    add_trade,
    remove_trade,
    get_portfolio_value,
    register_user,
    verify_user,
    get_all_users,
    delete_user,
    get_user_email,
    update_password,
    get_user_by_username_or_email
)
from src.alerts import send_alert_email
from src.sentiment_engine import analyze_sentiment
from src.portfolio_optimizer import optimize_portfolio
from src.theme_engine import apply_theme

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

NIFTY_BANK_SYMBOLS = {
    "HDFCBANK": "HDFC Bank Limited",
    "ICICIBANK": "ICICI Bank Limited",
    "SBIN": "State Bank of India",
    "KOTAKBANK": "Kotak Mahindra Bank Limited",
    "AXISBANK": "Axis Bank Limited",
    "INDUSINDBK": "IndusInd Bank Limited",
    "BANKBARODA": "Bank of Baroda",
    "AUBANK": "AU Small Finance Bank Limited",
    "FEDERALBNK": "The Federal Bank Limited",
    "IDFCFIRSTB": "IDFC First Bank Limited",
    "PNB": "Punjab National Bank",
    "BANDHANBNK": "Bandhan Bank Limited",
}

NIFTY_IT_SYMBOLS = {
    "INFY": "Infosys Limited",
    "TCS": "Tata Consultancy Services Limited",
    "HCLTECH": "HCL Technologies Limited",
    "WIPRO": "Wipro Limited",
    "TECHM": "Tech Mahindra Limited",
    "LTIM": "LTIMindtree Limited",
    "COFORGE": "Coforge Limited",
    "PERSISTENT": "Persistent Systems Limited",
    "MPHASIS": "Mphasis Limited",
    "LTTS": "L&T Technology Services Limited",
}

NIFTY_AUTO_SYMBOLS = {
    "MARUTI": "Maruti Suzuki India Limited",
    "TATAMOTORS": "Tata Motors Limited",
    "M&M": "Mahindra & Mahindra Limited",
    "BAJAJ-AUTO": "Bajaj Auto Limited",
    "HEROMOTOCO": "Hero MotoCorp Limited",
    "EICHERMOT": "Eicher Motors Limited",
    "TVSMOTOR": "TVS Motor Company Limited",
    "ASHOKLEY": "Ashok Leyland Limited",
    "BOSCHLTD": "Bosch Limited",
    "BALKRISIND": "Balkrishna Industries Limited",
    "MRF": "MRF Limited",
    "MOTHERSON": "Samvardhana Motherson International Limited"
}

NIFTY_FMCG_SYMBOLS = {
    "ITC": "ITC Limited",
    "HINDUNILVR": "Hindustan Unilever Limited",
    "NESTLEIND": "Nestle India Limited",
    "BRITANNIA": "Britannia Industries Limited",
    "TATACONSUM": "Tata Consumer Products Limited",
    "GODREJCP": "Godrej Consumer Products Limited",
    "DABUR": "Dabur India Limited",
    "MARICO": "Marico Limited",
    "VBL": "Varun Beverages Limited",
    "COLPAL": "Colgate-Palmolive (India) Limited",
    "UBL": "United Breweries Limited",
    "MCDOWELL-N": "United Spirits Limited"
}

NIFTY_METAL_SYMBOLS = {
    "TATASTEEL": "Tata Steel Limited",
    "JSWSTEEL": "JSW Steel Limited",
    "HINDALCO": "Hindalco Industries Limited",
    "COALINDIA": "Coal India Limited",
    "VEDL": "Vedanta Limited",
    "ADANIENT": "Adani Enterprises Limited",
    "SAIL": "Steel Authority of India Limited",
    "JINDALSTEL": "Jindal Steel & Power Limited",
    "NMDC": "NMDC Limited",
    "NATIONALUM": "National Aluminium Company Limited"
}

NIFTY_PHARMA_SYMBOLS = {
    "SUNPHARMA": "Sun Pharmaceutical Industries Limited",
    "CIPLA": "Cipla Limited",
    "DRREDDY": "Dr. Reddy's Laboratories Limited",
    "DIVISLAB": "Divi's Laboratories Limited",
    "LUPIN": "Lupin Limited",
    "AUROPHARMA": "Aurobindo Pharma Limited",
    "TORNTPHARM": "Torrent Pharmaceuticals Limited",
    "ALKEM": "Alkem Laboratories Limited",
    "BIOCON": "Biocon Limited",
    "GLENMARK": "Glenmark Pharmaceuticals Limited"
}

NIFTY_FINSRV_SYMBOLS = {
    "HDFCBANK": "HDFC Bank Limited",
    "ICICIBANK": "ICICI Bank Limited",
    "KOTAKBANK": "Kotak Mahindra Bank Limited",
    "AXISBANK": "Axis Bank Limited",
    "SBIN": "State Bank of India",
    "BAJFINANCE": "Bajaj Finance Limited",
    "BAJAJFINSV": "Bajaj Finserv Limited",
    "CHOLAFIN": "Cholamandalam Investment and Finance Company Limited",
    "HDFCAMC": "HDFC Asset Management Company Limited",
    "HDFCLIFE": "HDFC Life Insurance Company Limited",
    "SBILIFE": "SBI Life Insurance Company Limited",
    "ICICIGI": "ICICI Lombard General Insurance Company Limited",
    "ICICIPRULI": "ICICI Prudential Life Insurance Company Limited"
}

NIFTY_REALTY_SYMBOLS = {
    "DLF": "DLF Limited",
    "MACROTECH": "Macrotech Developers Limited",
    "GODREJPROP": "Godrej Properties Limited",
    "OBEROIRLTY": "Oberoi Realty Limited",
    "PRESTIGE": "Prestige Estates Projects Limited",
    "PHOENIXLTD": "The Phoenix Mills Limited",
    "BRIGADE": "Brigade Enterprises Limited",
    "SOBHA": "Sobha Limited"
}

MARKET_BASKETS = {
    "Nifty 50 (Bluechip)": NIFTY_50_SYMBOLS,
    "Nifty Bank": NIFTY_BANK_SYMBOLS,
    "Nifty IT": NIFTY_IT_SYMBOLS,
    "Nifty Auto": NIFTY_AUTO_SYMBOLS,
    "Nifty FMCG": NIFTY_FMCG_SYMBOLS,
    "Nifty Metal": NIFTY_METAL_SYMBOLS,
    "Nifty Pharma": NIFTY_PHARMA_SYMBOLS,
    "Nifty Financial Services": NIFTY_FINSRV_SYMBOLS,
    "Nifty Realty": NIFTY_REALTY_SYMBOLS
}

@st.cache_data(ttl=86400)
def get_sector(symbol: str) -> str:
    import yfinance as yf
    try:
        ticker = symbol if symbol.endswith(".NS") else f"{symbol}.NS"
        info = yf.Ticker(ticker).info
        return info.get("sector", "Unknown")
    except Exception:
        return "Unknown"


st.set_page_config(page_title="InvestIQ", layout="wide")
apply_theme()

def login_screen():
    import random
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>InvestIQ</h1>", unsafe_allow_html=True)
        
        if st.session_state.get("show_forgot_password", False):
            st.markdown("### Reset Password")
            if "reset_otp_pending" not in st.session_state:
                reset_user = st.text_input("Username or Email", key="reset_user")
                new_reset_pass = st.text_input("New Password", type="password", key="reset_pass")
                if st.button("Send Reset OTP", use_container_width=True, type="primary"):
                    if not reset_user or not new_reset_pass:
                        st.error("Please fill all fields.")
                    else:
                        user = get_user_by_username_or_email(reset_user)
                        if user and user.get("email"):
                            otp_code = str(random.randint(100000, 999999))
                            html = f"<h3>InvestIQ Password Reset</h3><p>Your password reset code is: <b>{otp_code}</b></p>"
                            with st.spinner("Sending OTP to registered email..."):
                                success, err_msg = send_alert_email(user["email"], "InvestIQ Password Reset", html)
                                if success:
                                    st.session_state["reset_otp_pending"] = True
                                    st.session_state["reset_otp_code"] = otp_code
                                    st.session_state["reset_pending_user"] = user["username"]
                                    st.session_state["reset_pending_pass"] = new_reset_pass
                                    st.rerun()
                                else:
                                    st.error("Failed to send email.")
                        else:
                            st.error("Account not found or no email associated.")
            else:
                st.info("OTP sent to your registered email.")
                entered_reset_otp = st.text_input("Enter 6-digit OTP", key="entered_reset_otp")
                c1, c2 = st.columns(2)
                if c1.button("Reset Password", type="primary", use_container_width=True):
                    if entered_reset_otp == st.session_state["reset_otp_code"]:
                        if update_password(st.session_state["reset_pending_user"], st.session_state["reset_pending_pass"]):
                            st.success("Password updated successfully! Please log in.")
                            for k in ["reset_otp_pending", "reset_otp_code", "reset_pending_user", "reset_pending_pass"]:
                                if k in st.session_state: del st.session_state[k]
                            st.session_state["show_forgot_password"] = False
                        else:
                            st.error("Failed to update password.")
                    else:
                        st.error("Invalid OTP.")
                if c2.button("Cancel Reset", use_container_width=True):
                    for k in ["reset_otp_pending", "reset_otp_code", "reset_pending_user", "reset_pending_pass"]:
                        if k in st.session_state: del st.session_state[k]
                    st.rerun()
            
            st.divider()
            if st.button("Back to Login", use_container_width=True):
                st.session_state["show_forgot_password"] = False
                st.rerun()
                
        else:
            tab1, tab2 = st.tabs(["Login", "Sign Up"])
            
            with tab1:
                st.markdown("### Welcome Back")
                username = st.text_input("Username", key="login_user")
                password = st.text_input("Password", type="password", key="login_pass")
                
                st.write("") # spacer
                
                if st.button("Login", use_container_width=True, type="primary"):
                    user = verify_user(username, password)
                    if user:
                        st.session_state["user_id"] = user["id"]
                        st.session_state["username"] = user["username"]
                        st.session_state["email"] = user["email"]
                        st.session_state["role"] = user["role"]
                        st.session_state["ui_theme"] = user.get("ui_theme", "Sunset Glow (Light)")
                        st.session_state["profile_pic"] = user.get("profile_pic")
                        cookie_controller.set("investiq_session", user["username"], max_age=86400*30)
                        st.success("Login Successful! Initializing dashboard...")
                        st.components.v1.html("<script>setTimeout(function() { window.parent.location.reload(); }, 1000);</script>", height=0)
                        # Remove st.rerun() to ensure component is flushed to browser
                    else:
                        st.error("Invalid credentials.")
                
                st.write("") # spacer
                if st.button("Forgot Password?", use_container_width=True):
                    st.session_state["show_forgot_password"] = True
                    st.rerun()
                        
            with tab2:
                st.markdown("### Create Account")
                if "otp_pending" not in st.session_state:
                    new_user = st.text_input("New Username", key="signup_user")
                    new_email = st.text_input("Email Address", key="signup_email")
                    new_pass = st.text_input("New Password", type="password", key="signup_pass")
                    if st.button("Send OTP", use_container_width=True, type="primary"):
                        if not new_email or "@" not in new_email:
                            st.error("Please enter a valid email address.")
                        elif not new_user or not new_pass:
                            st.error("Please fill all fields.")
                        else:
                            otp_code = str(random.randint(100000, 999999))
                            html = f"<h3>InvestIQ Verification</h3><p>Your verification code is: <b>{otp_code}</b></p>"
                            with st.spinner("Sending OTP via Email..."):
                                success, err_msg = send_alert_email(new_email, "InvestIQ Verification Code", html)
                                if success:
                                    st.session_state["otp_pending"] = True
                                    st.session_state["otp_code"] = otp_code
                                    st.session_state["pending_user"] = new_user
                                    st.session_state["pending_email"] = new_email
                                    st.session_state["pending_pass"] = new_pass
                                    st.rerun()
                                else:
                                    st.error(f"Failed to send OTP. Check SMTP settings. Error: {err_msg}")
                else:
                    st.info(f"An OTP was sent to **{st.session_state['pending_email']}**.")
                    entered_otp = st.text_input("Enter 6-digit OTP", key="entered_otp")
                    c1, c2 = st.columns(2)
                    if c1.button("Verify & Sign Up", type="primary", use_container_width=True):
                        if entered_otp == st.session_state["otp_code"]:
                            if register_user(st.session_state["pending_user"], st.session_state["pending_email"], st.session_state["pending_pass"]):
                                st.success("Account created successfully! You can now log in.")
                                for k in ["otp_pending", "otp_code", "pending_user", "pending_email", "pending_pass"]:
                                    if k in st.session_state: del st.session_state[k]
                            else:
                                st.error("Username already exists or database error.")
                        else:
                            st.error("Invalid OTP. Try again.")
                    if c2.button("Cancel", use_container_width=True):
                        for k in ["otp_pending", "otp_code", "pending_user", "pending_email", "pending_pass"]:
                            if k in st.session_state: del st.session_state[k]
                        st.rerun()

from streamlit_cookies_controller import CookieController
cookie_controller = CookieController()

if "user_id" not in st.session_state:
    session_cookie = cookie_controller.get("investiq_session")
    if session_cookie:
        from src.portfolio_manager import get_user_by_username
        user = get_user_by_username(session_cookie)
        if user:
            st.session_state["user_id"] = user["id"]
            st.session_state["username"] = user["username"]
            st.session_state["email"] = user["email"]
            st.session_state["role"] = user["role"]
            st.session_state["ui_theme"] = user.get("ui_theme", "Sunset Glow (Light)")
            st.session_state["profile_pic"] = user.get("profile_pic")
            st.rerun()

if "user_id" not in st.session_state:
    login_screen()
    st.stop()

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "dashboard"

with st.sidebar:
    # 1. Professional User Profile Card
    if st.session_state.get("profile_pic"):
        profile_html = f'<img src="data:image/png;base64,{st.session_state["profile_pic"]}" style="width: 48px; height: 48px; border-radius: 50%; object-fit: cover; box-shadow: 0 2px 4px rgba(0,0,0,0.1); flex-shrink: 0; border: 2px solid var(--accent-color);">'
    else:
        profile_html = f'<div style="width: 48px; height: 48px; border-radius: 50%; background: linear-gradient(135deg, var(--accent-color), #3b82f6); color: white; display: flex; justify-content: center; align-items: center; font-size: 1.5rem; font-weight: 700; flex-shrink: 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">{st.session_state.get("username", "U")[0].upper()}</div>'

    st.markdown(f"""
    <div style="padding: 16px; border-radius: 12px; background: linear-gradient(135deg, var(--bg-card), var(--bg-primary)); border: 1px solid var(--border-color); display: flex; align-items: center; gap: 16px; margin-bottom: 24px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
        {profile_html}
        <div style="overflow: hidden;">
            <div style="font-weight: 700; color: var(--text-primary); font-size: 1.1rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{st.session_state.get('username', 'Unknown').upper()}</div>
            <div style="color: var(--text-secondary); font-size: 0.85rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">{st.session_state.get('role', 'User')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Sleek Navigation
    st.markdown("<div style='font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>Navigation</div>", unsafe_allow_html=True)
    
    nav_options = {"Dashboard": ":material/dashboard: Dashboard", "My Profile": ":material/person: My Profile", "Settings": ":material/settings: Settings"}
    current_nav = "Dashboard"
    if st.session_state["current_page"] == "profile": current_nav = "My Profile"
    elif st.session_state["current_page"] == "settings": current_nav = "Settings"
    
    selected_nav = st.radio(
        "Navigation",
        options=list(nav_options.keys()),
        format_func=lambda x: nav_options[x],
        index=list(nav_options.keys()).index(current_nav),
        label_visibility="collapsed"
    )
    
    if selected_nav == "Dashboard" and st.session_state["current_page"] != "dashboard":
        st.session_state["current_page"] = "dashboard"
        st.rerun()
    elif selected_nav == "My Profile" and st.session_state["current_page"] != "profile":
        st.session_state["current_page"] = "profile"
        st.rerun()
    elif selected_nav == "Settings" and st.session_state["current_page"] != "settings":
        st.session_state["current_page"] = "settings"
        st.rerun()
        
    st.write("")
    st.markdown('<div class="logout-btn-wrapper"></div>', unsafe_allow_html=True)
    if st.button(":material/logout: Logout", use_container_width=True, type="secondary"):
        cookie_controller.remove("investiq_session")
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.components.v1.html("<script>setTimeout(function() { window.parent.location.reload(); }, 500);</script>", height=0)
        st.stop()


if st.session_state["current_page"] == "dashboard":
    st.title("InvestIQ")
    st.caption("NSE-focused analytics dashboard")
    st.info(
        "Market data is near real-time and typically delayed by the upstream source (usually minutes, not tick-by-tick live)."
    )


    def _signal_color(signal: str) -> str:
        if signal == "BUY":
            return "#10B981" # Emerald Green
        if signal == "SELL":
            return "#EF4444" # Red
        return "#EAB308" # Golden Yellow (readable on light and dark)


    def _render_candles(df: pd.DataFrame, symbol: str) -> None:
        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=df.index,
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                    name=symbol,
                )
            ]
        )
        fig.update_layout(
            title=f"{symbol} Price",
            xaxis_title="Date",
            yaxis_title="Price",
            xaxis_rangeslider_visible=False,
            height=460,
        )
        st.plotly_chart(fig, use_container_width=True)


    def _render_quote_strip(df: pd.DataFrame, symbol: str) -> None:
        latest = df.iloc[-1]
        latest_close = float(latest["close"])
        latest_open = float(latest["open"])
        latest_high = float(latest["high"])
        latest_low = float(latest["low"])

        if len(df) > 1:
            prev_close = float(df["close"].iloc[-2])
        else:
            prev_close = latest_close

        change = latest_close - prev_close
        change_pct = (change / prev_close * 100.0) if prev_close != 0 else 0.0
        up = change >= 0
        color = "#15803d" if up else "#b91c1c"
        arrow = "▲" if up else "▼"
        now_ist = datetime.now(ZoneInfo("Asia/Kolkata"))
        ts_ist = now_ist.strftime("%d-%b-%Y %I:%M:%S %p IST")

        # NSE equity regular session (approx): 09:15 to 15:30 IST, Mon-Fri.
        # This is a practical local rule and may differ on special sessions/holidays.
        in_week = now_ist.weekday() < 5
        hhmm = now_ist.hour * 60 + now_ist.minute
        market_open = 9 * 60 + 15
        market_close = 15 * 60 + 30
        is_open_session = in_week and (market_open <= hhmm <= market_close)
        session_label = "Open" if is_open_session else "Market Day Closed"
        session_color = "#15803d" if is_open_session else "#b91c1c"

        st.markdown(
            f"""
            <div style="border:1px solid #e2e8f0;border-radius:12px;padding:14px 16px;margin-bottom:12px;background:#f8fafc;">
              <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
                <div style="font-size:1.65rem;font-weight:700;color:#0f172a;">{symbol.upper()} (EQ)</div>
                <div style="display:flex;gap:14px;align-items:center;flex-wrap:wrap;">
                  <div style="font-size:0.95rem;color:#334155;">As on {ts_ist} (all prices in ₹)</div>
                  <div style="font-size:0.95rem;font-weight:700;color:{session_color};">Session: {session_label}</div>
                </div>
              </div>
              <div style="display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;margin-top:4px;">
                <div style="font-size:2.2rem;font-weight:700;color:#0f172a;">₹{latest_close:,.2f}</div>
                <div style="font-size:1.8rem;font-weight:700;color:{color};">{arrow}</div>
                <div style="font-size:2rem;font-weight:700;color:{color};">{change:,.2f} ({change_pct:,.2f}%)</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        q1, q2, q3, q4, q5 = st.columns(5)
        q1.metric("Prev Close", f"{prev_close:,.2f}")
        q2.metric("Open", f"{latest_open:,.2f}")
        q3.metric("High", f"{latest_high:,.2f}")
        q4.metric("Low", f"{latest_low:,.2f}")
        if is_open_session:
            q5.metric("Official Close", "-")
        else:
            q5.metric("Official Close", f"{latest_close:,.2f}", f"{change:,.2f} ({change_pct:,.2f}%)")


    @st.cache_data(ttl=300, show_spinner=False)
    def get_dynamic_best_model(symbol_input, period):
        comp_df = get_stock_data(symbol_input, period=period)
        if comp_df is None or comp_df.empty: return "Linear Regression"
        enriched_comp = apply_indicators(comp_df)
        if enriched_comp is None: return "Linear Regression"
        results = compare_all_models(enriched_comp, lookback=60, test_size=0.2)
        if not results: return "Linear Regression"
    
        best_acc = -1
        best_model = "Linear Regression"
        for m_name, metrics in results["models"].items():
            if "error" not in metrics:
                acc = float(str(metrics["Direction Accuracy"]).rstrip('%'))
                if acc > best_acc:
                    best_acc = acc
                    best_model = m_name
        return best_model

    @st.cache_data(ttl=300, show_spinner=False)
    def get_optimal_stop_loss(symbol_input, period):
        comp_df = get_stock_data(symbol_input, period=period)
        if comp_df is None or comp_df.empty or len(comp_df) < 20: return 5.0
    
        import pandas_ta as ta
        if "high" in comp_df.columns and "low" in comp_df.columns and "close" in comp_df.columns:
            atr = ta.atr(comp_df["high"], comp_df["low"], comp_df["close"], length=14)
            if atr is not None and not atr.empty and not pd.isna(atr.iloc[-1]):
                latest_atr = atr.iloc[-1]
                latest_close = comp_df["close"].iloc[-1]
                opt_sl = float((latest_atr * 2 / latest_close) * 100)
                return round(max(1.0, min(20.0, opt_sl)), 1)
            
        recent_data = comp_df["close"].tail(20)
        daily_returns = recent_data.pct_change().dropna()
        if daily_returns.empty: return 5.0
    
        std = daily_returns.std()
        opt_sl = float(std * 2 * 100)
        return round(max(1.0, min(20.0, opt_sl)), 1)

    @st.cache_data(ttl=60 * 60 * 12)
    def _load_nse_symbol_master() -> pd.DataFrame:
        url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        raw = pd.read_csv(StringIO(response.text))
        raw.columns = [str(c).strip().upper() for c in raw.columns]
        if "SYMBOL" not in raw.columns or "NAME OF COMPANY" not in raw.columns:
            raise ValueError("Unexpected NSE symbol master format")
        out = raw[["SYMBOL", "NAME OF COMPANY"]].copy()
        out["SYMBOL"] = out["SYMBOL"].astype(str).str.strip().str.upper()
        out["NAME OF COMPANY"] = out["NAME OF COMPANY"].astype(str).str.strip()
        out = out.drop_duplicates(subset=["SYMBOL"]).sort_values("SYMBOL").reset_index(drop=True)
        return out


    if st.session_state["current_page"] == "dashboard":
        with st.sidebar:
            st.divider()
            st.markdown("<div style='font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;'>Market Controls</div>", unsafe_allow_html=True)
            try:
                nse_master = _load_nse_symbol_master()
                symbols = nse_master["SYMBOL"].tolist()
                default_idx = symbols.index("RELIANCE") if "RELIANCE" in symbols else 0
                symbol_input = st.selectbox("Stock Symbol (NSE)", symbols, index=default_idx)
                company_name = nse_master.loc[nse_master["SYMBOL"] == symbol_input, "NAME OF COMPANY"].iloc[0]
                st.caption(f"Company: {company_name}")
            except Exception:
                st.warning("Could not load full NSE list right now; using manual symbol input fallback.")
                symbol_input = st.text_input("Stock Symbol (NSE)", value="RELIANCE")
            
            period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=4)
        
            with st.spinner("Dynamically determining best model..."):
                model_type = get_dynamic_best_model(symbol_input, period)
                opt_sl = get_optimal_stop_loss(symbol_input, period)
            st.info(f"Dynamically Selected Best Model: **{model_type}**")
        
            risk_pct = st.slider("Risk % per trade", 0.5, 5.0, 2.0, 0.5)
            capital = st.number_input("Capital", min_value=1000.0, value=100000.0, step=10000.0)
            stop_loss_pct = st.slider("Stop Loss % (Optimized via 2x ATR)", 1.0, 20.0, float(opt_sl), 0.5)


    is_admin = st.session_state["role"] == "admin"
    if is_admin:
        tabs = st.tabs(["Admin Panel", "Market View", "Trade Screener", "Compare Models"])
        tab_admin, tab_market, tab_screener, tab_compare = tabs[0], tabs[1], tabs[2], tabs[3]
        tab_backtest = tab_strategy = tab_portfolio = None
    else:
        tabs = st.tabs(["Market View", "Trade Screener", "Backtest", "Strategy Builder", "Portfolio", "Compare Models"])
        tab_market, tab_screener, tab_backtest, tab_strategy, tab_portfolio, tab_compare = tabs[0], tabs[1], tabs[2], tabs[3], tabs[4], tabs[5]
        tab_admin = None


    if tab_market:
        with tab_market:
            with st.spinner(f"Fetching market data for {symbol_input}..."):
                df = get_stock_data(symbol_input, period=period)
            if df is None or df.empty:
                st.error("Could not fetch stock data. Please check the symbol and try again.")
            else:
                _render_quote_strip(df, symbol_input)
                enriched = apply_indicators(df)
                if enriched is None:
                    st.error("Could not compute indicators.")
                else:
                    _render_candles(enriched, symbol_input.upper())

                    signal = generate_signal(enriched)
                    latest_close = float(enriched["close"].iloc[-1])
                    stop_loss_price = latest_close * (1 - stop_loss_pct / 100.0)
                    sizing = calculate_position_size(
                        capital=capital,
                        risk_pct=risk_pct,
                        stop_loss=stop_loss_price,
                        current_price=latest_close,
                    )
                    with st.spinner(f"Running {model_type} model..."):
                        pred = predict_price(enriched, lookback=60, test_size=0.2, model_type=model_type)

                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Latest Close", f"{latest_close:.2f}")
                    c2.markdown(
                        f"""
                        <style>
                        .signal-card-box {{
                            background-color: var(--bg-card);
                            padding: 15px 20px;
                            border-radius: 12px;
                            box-shadow: 0 4px 6px var(--shadow-color);
                            border: 1px solid var(--border-color);
                            display: flex;
                            flex-direction: column;
                            transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1), box-shadow 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
                        }}
                        .signal-card-box:hover {{
                            transform: translateY(-8px);
                            box-shadow: 0 12px 20px var(--shadow-color-hover);
                        }}
                        .signal-text-val {{
                            font-size: 1.8rem;
                            font-weight: 700;
                            line-height: 1.2;
                        }}
                        #signal-val-BUY {{ color: #10B981 !important; }}
                        #signal-val-SELL {{ color: #EF4444 !important; }}
                        #signal-val-HOLD {{ color: #EAB308 !important; }}
                        </style>
                        <div class="signal-card-box">
                            <div style="color: var(--text-secondary); font-weight: 600; font-size: 0.875rem; margin-bottom: 5px;">AI Trading Signal</div>
                            <div class="signal-text-val" id="signal-val-{signal}">
                                {signal}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if pred is not None:
                        c3.metric(f"Predicted Next Close ({model_type})", f"{pred['predicted_close']:.2f}")
                        c4.metric("Model MAE", f"{pred['mae']:.2f} ({pred['mae_pct_of_price']:.2f}%)")
                    else:
                        c3.metric("Predicted Next Close", "N/A")
                        c4.metric("Model MAE", "N/A")
                        st.caption("Prediction may be unavailable when selected period has too few rows.")

                    st.subheader("Position Sizing")
                    s1, s2, s3 = st.columns(3)
                    s1.metric("Risk Amount", f"{sizing['risk_amount']:.2f}")
                    s2.metric("Suggested Shares", f"{int(sizing['shares'])}")
                    s3.metric("Position Value", f"{sizing['position_value']:.2f}")
            
                    st.divider()
            
                    # --- Live News & Sentiment ---
                    st.subheader("Live News & NLP Sentiment")
                    with st.spinner("Fetching live news and analyzing sentiment..."):
                        sentiment_data = analyze_sentiment(symbol_input)
                
                    overall_label = sentiment_data["overall_label"]
                    overall_comp = sentiment_data["overall_compound"]
            
                    if "Bullish" in overall_label:
                        color = "green"
                    elif "Bearish" in overall_label:
                        color = "red"
                    else:
                        color = "gray"
                
                    st.markdown(
                        f"<h4>Overall Market Sentiment: <span style='color:{color}'>{overall_label}</span> (Score: {overall_comp * 100:+.0f}%)</h4>",
                        unsafe_allow_html=True
                    )
            
                    articles = sentiment_data["articles"]
                    if not articles:
                        st.info("No recent news headlines found for this ticker.")
                    else:
                        with st.expander(f"View Latest Headlines ({len(articles)})", expanded=True):
                            for idx, art in enumerate(articles):
                                art_lbl = art['label']
                                art_col = "green" if art_lbl == "Bullish" else "red" if art_lbl == "Bearish" else "gray"
                        
                                st.markdown(f"**{idx+1}. {art['title']}**")
                                st.caption(f"Source: {art['publisher']} | NLP Score: <span style='color:{art_col}'>{art_lbl} ({art['compound'] * 100:+.0f}%)</span>", unsafe_allow_html=True)
                                if art['link']:
                                    st.markdown(f"[Read Article]({art['link']})")
                                st.write("---")

    if tab_screener:
        with tab_screener:
            st.header("Trade Screener")
            st.write("Scan market baskets for active BUY and SELL signals.")
            
            # Select Basket
            selected_basket_name = st.selectbox("Select Market Basket to Scan", list(MARKET_BASKETS.keys()))
            selected_basket_dict = MARKET_BASKETS[selected_basket_name]
            
            if st.button(f"Run {selected_basket_name} Scan", type="primary"):
                with st.spinner(f"Scanning {selected_basket_name} stocks (this may take up to 30 seconds)..."):
                    results = []
                    
                    # Create a progress bar
                    progress_text = "Scanning companies..."
                    my_bar = st.progress(0, text=progress_text)
                    
                    symbols_list = list(selected_basket_dict.keys())
                    total_symbols = len(symbols_list)
                    
                    for idx, sym in enumerate(symbols_list):
                        # Update progress
                        my_bar.progress((idx + 1) / total_symbols, text=f"Scanning {sym} ({idx + 1}/{total_symbols})...")
                        
                        try:
                            df_scan = get_stock_data(sym, period="1y")
                            if df_scan is not None and not df_scan.empty:
                                df_enc = apply_indicators(df_scan)
                                if df_enc is not None:
                                    sig = generate_signal(df_enc)
                                    if sig in ["BUY", "SELL"]:
                                        latest_close_scan = float(df_enc["close"].iloc[-1])
                                        stop_loss_price_scan = latest_close_scan * (1 - stop_loss_pct / 100.0)
                                        sizing_scan = calculate_position_size(
                                            capital=capital,
                                            risk_pct=risk_pct,
                                            stop_loss=stop_loss_price_scan,
                                            current_price=latest_close_scan,
                                        )
                                        results.append({
                                            "Symbol": sym,
                                            "Company Name": selected_basket_dict[sym],
                                            "Signal": sig,
                                            "Latest Close": f"₹{latest_close_scan:.2f}",
                                            "Suggested Shares": int(sizing_scan['shares']),
                                            "Position Value": f"₹{sizing_scan['position_value']:.2f}"
                                        })
                        except Exception as e:
                            pass # Skip failures during bulk scan
                    
                    my_bar.empty()
                    
                    if not results:
                        st.info("No active BUY or SELL signals found across the Nifty 50 at this time.")
                    else:
                        st.success(f"Scan complete! Found {len(results)} actionable signals.")
                        
                        # Convert to DataFrame for nice display
                        res_df = pd.DataFrame(results)
                        
                        st.dataframe(
                            res_df,
                            use_container_width=True,
                            hide_index=True
                        )

    if tab_compare:
        with tab_compare:
            st.header("Compare Machine Learning Models")
            st.write("Run a side-by-side comparison of all prediction models on the selected stock and time period.")
    
            if st.button("Run Comparison", type="primary"):
                with st.spinner("Training and comparing models..."):
                    comp_df = get_stock_data(symbol_input, period=period)
                    if comp_df is None or comp_df.empty:
                        st.error("Could not fetch stock data for comparison.")
                    else:
                        enriched_comp = apply_indicators(comp_df)
                        if enriched_comp is None:
                            st.error("Not enough data to run comparison.")
                        else:
                            results = compare_all_models(enriched_comp, lookback=60, test_size=0.2)
                            if not results:
                                st.error("Model comparison failed. Check data length.")
                            else:
                                test_dates = results["test_dates"]
                                y_true = results["y_true"]
                                models = results["models"]
                        
                                # Build DataFrame
                                summary = []
                                for m_name, metrics in models.items():
                                    if "error" in metrics:
                                        st.error(f"{m_name} Error: {metrics['error']}")
                                        continue
                                    summary.append({
                                        "Model": m_name,
                                        "MAE": round(metrics["MAE"], 2),
                                        "RMSE": round(metrics["RMSE"], 2),
                                        "MAPE": f"{metrics['MAPE']:.2f}%",
                                        "Direction Accuracy": f"{metrics['Direction Accuracy']*100:.1f}%",
                                        "F1 Score": round(metrics["F1 Score"], 2)
                                    })
                        
                                if summary:
                                    # 1. Main Line Chart: Actual vs Predicted
                                    st.subheader("Actual vs Predicted Price (Test Set)")
                                    fig_line = go.Figure()
                                    fig_line.add_trace(go.Scatter(x=test_dates, y=y_true, mode="lines", name="Actual True Price", line=dict(color='black', width=3)))
                            
                                    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
                                    for i, row in enumerate(summary):
                                        m_name = row["Model"]
                                        y_pred = models[m_name]["y_pred"]
                                        fig_line.add_trace(go.Scatter(x=test_dates, y=y_pred, mode="lines", name=m_name, line=dict(color=colors[i%3], dash='dash')))
                                
                                    fig_line.update_layout(height=500, xaxis_title="Date", yaxis_title="Price", hovermode="x unified")
                                    st.plotly_chart(fig_line, use_container_width=True)

                                    # 2. Performance Metrics
                                    st.subheader("Performance Metrics Overview")
                                    sum_df = pd.DataFrame(summary)
                            
                                    m_cols = st.columns(3)
                                    # Best Model Logic
                                    best_mae = sum_df.loc[sum_df["MAE"].idxmin()]["Model"]
                                    best_acc = sum_df.loc[sum_df["Direction Accuracy"].str.rstrip('%').astype(float).idxmax()]["Model"]
                                    best_mape = sum_df.loc[sum_df["MAPE"].str.rstrip('%').astype(float).idxmin()]["Model"]
                            
                                    m_cols[0].metric("Lowest MAE", best_mae)
                                    m_cols[1].metric("Highest Accuracy", best_acc)
                                    m_cols[2].metric("Lowest MAPE", best_mape)

                                    # Side-by-Side Bar Charts
                                    b1, b2 = st.columns(2)
                                    with b1:
                                        fig_mae = px.bar(sum_df, x="Model", y="MAE", color="Model", title="Mean Absolute Error (Lower is Better)")
                                        st.plotly_chart(fig_mae, use_container_width=True)
                                    with b2:
                                        # Clean Accuracy string for plotting
                                        acc_vals = sum_df["Direction Accuracy"].str.rstrip('%').astype(float)
                                        temp_df = sum_df.copy()
                                        temp_df["Accuracy %"] = acc_vals
                                        fig_acc = px.bar(temp_df, x="Model", y="Accuracy %", color="Model", title="Directional Accuracy (Higher is Better)")
                                        st.plotly_chart(fig_acc, use_container_width=True)

                                    st.dataframe(sum_df.set_index("Model"), use_container_width=True)
                            
                                    # 3. Heatmaps for Confusion Matrix
                                    st.subheader("Confusion Matrices (Up vs Down Direction)")
                                    cols = st.columns(len(summary))
                                    for i, row in enumerate(summary):
                                        m_name = row["Model"]
                                        cm = models[m_name]["CM"]
                                        with cols[i]:
                                            st.markdown(f"**{m_name}**")
                                            fig_cm = px.imshow(cm, text_auto=True, color_continuous_scale="Blues",
                                                               x=["Pred Down", "Pred Up"], y=["Actual Down", "Actual Up"])
                                            fig_cm.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20), coloraxis_showscale=False)
                                            st.plotly_chart(fig_cm, use_container_width=True, key=f"cm_heatmap_{m_name}_{i}")

    if tab_portfolio:
        with tab_portfolio:
            st.subheader("Holdings")
            summary_data = get_portfolio_value(st.session_state["user_id"])
            positions = summary_data["positions"]
    
            st.subheader("Current Holdings")
            if positions:
                df_pos = pd.DataFrame(positions)
                st.dataframe(df_pos, use_container_width=True)
        
                st.divider()
                st.subheader("Portfolio Analytics")
        
                # CSV Export
                csv_data = df_pos.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Portfolio as CSV",
                    data=csv_data,
                    file_name="investiq_portfolio.csv",
                    mime="text/csv",
                )
        
                # Sector Pie Chart
                with st.spinner("Analyzing Sector Allocation..."):
                    import plotly.express as px
                    sector_data = []
                    for p in positions:
                        sector = get_sector(p["symbol"])
                        val = p["market_value"] if p["market_value"] is not None else p["total_cost"]
                        sector_data.append({"Sector": sector, "Value": val})
                
                    if sector_data:
                        df_sectors = pd.DataFrame(sector_data).groupby("Sector", as_index=False)["Value"].sum()
                        fig = px.pie(df_sectors, values="Value", names="Sector", hole=0.4, 
                                     color_discrete_sequence=px.colors.qualitative.Pastel)
                        fig.update_layout(margin=dict(t=30, b=0, l=0, r=0))
                        st.plotly_chart(fig, use_container_width=True)
                
                st.divider()
                st.subheader("AI Portfolio Optimizer (Modern Portfolio Theory)")
                st.write("Calculate the mathematically optimal weights to maximize your Sharpe Ratio.")
        
                if st.button("Run Markowitz Optimization", type="primary"):
                    syms = list(set([p["symbol"] for p in positions]))
                    if len(syms) < 2:
                        st.warning("You need at least 2 distinct stocks in your portfolio to run optimization!")
                    else:
                        with st.spinner("Downloading 1-Year historical data and running Scipy Optimizer..."):
                            opt_res = optimize_portfolio(syms)
                    
                        if opt_res.get("error"):
                            st.error(opt_res["error"])
                        else:
                            opt_w = opt_res["optimal_weights"]
                            st.success(f"Optimization Complete! Expected Annual Return: **{opt_res['expected_return']:.2f}%** | Volatility: **{opt_res['expected_volatility']:.2f}%** | Max Sharpe Ratio: **{opt_res['sharpe_ratio']:.2f}**")
                    
                            total_val = sum([p["market_value"] if p["market_value"] else p["total_cost"] for p in positions])
                            current_w = {}
                            for p in positions:
                                s = p["symbol"]
                                v = p["market_value"] if p["market_value"] else p["total_cost"]
                                current_w[s] = current_w.get(s, 0) + (v / total_val * 100)
                        
                            comp_data = []
                            for s in syms:
                                comp_data.append({"Symbol": s, "Allocation": current_w.get(s, 0), "Type": "Current (%)"})
                                comp_data.append({"Symbol": s, "Allocation": opt_w.get(s, 0), "Type": "Optimal (%)"})
                        
                            df_comp = pd.DataFrame(comp_data)
                            import plotly.express as px
                            fig_comp = px.bar(df_comp, x="Symbol", y="Allocation", color="Type", barmode="group",
                                              title="Current vs Optimal Portfolio Allocation",
                                              color_discrete_map={"Current (%)": "#94a3b8", "Optimal (%)": "#10b981"},
                                              text_auto=".1f")
                            fig_comp.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                            st.plotly_chart(fig_comp, use_container_width=True)
                    
                            # --- AI Recommendations Table ---
                            st.markdown("### 🤖 Actionable AI Recommendations")
                            table_data = []
                            for s in syms:
                                curr_alloc = current_w.get(s, 0)
                                opt_alloc = opt_w.get(s, 0)
                                diff = opt_alloc - curr_alloc
                                if opt_alloc < 0.1: action = "🚨 Exit Position"
                                elif diff > 5: action = "📈 Buy More"
                                elif diff < -5: action = "📉 Reduce Position"
                                else: action = "⚖️ Hold"
                        
                                table_data.append({
                                    "Stock Symbol": s,
                                    "Current %": f"{curr_alloc:.1f}%",
                                    "Target %": f"{opt_alloc:.1f}%",
                                    "AI Suggestion": action
                                })
                            st.dataframe(pd.DataFrame(table_data), use_container_width=True)
                            st.info("💡 **Why is a bar missing?** If a stock has an **Optimal % of 0.0**, the Markowitz algorithm has determined that the asset carries too much mathematical risk compared to its expected return, and suggests you completely sell it to protect your portfolio.")
                
            else:
                st.info("No open positions.")

            st.subheader("Add Trade")
            with st.form("add_trade_form"):
                a_symbol = st.text_input("Symbol", value=symbol_input, key="add_symbol")
                st.caption(f"Using current selected symbol by default: {symbol_input}")
                a_qty = st.number_input("Quantity", min_value=1, value=10, step=1, key="add_qty")
                a_price = st.number_input("Buy Price", min_value=0.01, value=1000.0, step=0.5, key="add_price")
                add_submit = st.form_submit_button("Add Trade")
                if add_submit:
                    try:
                        trade_id = add_trade(st.session_state["user_id"], a_symbol, int(a_qty), float(a_price))
                        st.success(f"Trade added with ID {trade_id}")
                    except Exception as exc:
                        st.error(f"Failed to add trade: {exc}")

            st.subheader("Remove Trade")
            with st.form("remove_trade_form"):
                r_trade_id = st.number_input("Trade ID", min_value=1, value=1, step=1)
                remove_submit = st.form_submit_button("Remove Trade")
                if remove_submit:
                    ok = remove_trade(st.session_state["user_id"], int(r_trade_id))
                    if ok:
                        st.success("Trade removed.")
                    else:
                        st.warning("Trade ID not found.")

            st.subheader("Portfolio Value")
            summary = get_portfolio_value(st.session_state["user_id"])
            positions = summary["positions"]
            if positions:
                df_pos = pd.DataFrame(positions)
                df_pos.rename(columns={
                    "id": "Trade ID", "symbol": "Ticker", "qty": "Shares",
                    "avg_price": "Avg Buy Price", "total_cost": "Total Invested",
                    "market_value": "Current Value", "pnl": "Profit/Loss", "pnl_pct": "Return (%)"
                }, inplace=True)
                st.dataframe(df_pos, use_container_width=True, hide_index=True)
            st.metric("Total Cost", f"{summary['total_cost']:.2f}")
            st.metric(
                "Total Market Value",
                "N/A" if summary["total_market_value"] is None else f"{summary['total_market_value']:.2f}",
            )
            st.metric("Total P&L", "N/A" if summary["total_pnl"] is None else f"{summary['total_pnl']:.2f}")

            st.subheader("Automated Alerts")
            st.write("Scan your portfolio and receive an email with AI trading signals.")
            if st.button("Scan Portfolio & Send Alert", type="primary"):
                if not st.session_state.get("email") or st.session_state["email"] == "admin@investiq.local":
                    st.error("Your account does not have a valid email setup. Please create a new account with a real email.")
                elif not positions:
                    st.warning("Your portfolio is empty. Add trades to receive alerts!")
                else:
                    with st.spinner("Scanning portfolio..."):
                        signals = []
                        for p in positions:
                            symbol = p["symbol"]
                            df = get_stock_data(symbol, period="1mo")
                            if df is not None:
                                df_enc = apply_indicators(df)
                                if df_enc is not None:
                                    sig = generate_signal(df_enc)
                                    if sig in ["BUY", "SELL"]:
                                        signals.append(f"<b>{symbol}</b>: <span style='color:{'green' if sig=='BUY' else 'red'}'>{sig}</span>")
                
                        if not signals:
                            st.info("No actionable BUY or SELL signals detected in your portfolio today.")
                        else:
                            html_body = "<h3>InvestIQ Portfolio Alert</h3><ul>" + "".join([f"<li>{s}</li>" for s in signals]) + "</ul>"
                            success, err_msg = send_alert_email(st.session_state["email"], "InvestIQ Trading Signals", html_body)
                            if success:
                                st.success(f"Alert sent successfully to {st.session_state['email']}!")
                            else:
                                st.error(f"Failed to send email. Check your SMTP secrets. Error: {err_msg}")

    if tab_backtest:
        with tab_backtest:
            st.subheader(f"Machine Learning Backtest ({model_type})")
            st.caption(f"Strategy: Buy if {model_type} predicts positive return for tomorrow, otherwise stay in cash.")
            st.caption("Out-Of-Sample backtest uses the last 20% of the selected time period (Test Set only).")

            with st.spinner(f"Preparing ML Backtest for {model_type}..."):
                bt_df = get_stock_data(symbol_input, period=period)
                if bt_df is not None and not bt_df.empty:
                    enriched_bt = apply_indicators(bt_df)
                    if enriched_bt is not None:
                        ml_pred = predict_price(enriched_bt, lookback=60, test_size=0.2, model_type=model_type)
    
            if 'ml_pred' not in locals() or ml_pred is None:
                st.error("Could not run ML prediction for backtest. Please check data length.")
            else:
                with st.spinner("Simulating Equity Curve..."):
                    bt_result = run_ml_backtest_v2(
                        bt_df,
                        test_dates=ml_pred["test_dates"],
                        y_pred_ret_test=ml_pred["y_pred_ret_test"],
                        drop_incomplete_last_candle=True,
                    )
                if bt_result is None:
                    st.error("Not enough trades or data to simulate backtest.")
                else:
                    summary = bt_result["summary"]
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Total Return", f"{summary['total_return_pct']:.2f}%")
                    c2.metric("Win Rate", f"{summary['win_rate_pct']:.2f}%")
                    c3.metric("Max Drawdown", f"{summary['max_drawdown_pct']:.2f}%")
                    c4.metric("Closed Trades", str(summary["num_closed_trades"]))

                    eq = bt_result["equity_curve"]
                    fig = go.Figure(data=[go.Scatter(x=eq.index, y=eq["equity_curve"], mode="lines", name="Equity")])
                    fig.update_layout(
                        title=f"{symbol_input.upper()} True OOS ML Equity Curve",
                        xaxis_title="Date",
                        yaxis_title="Equity (start=1.0)",
                        height=420,
                    )
                    st.plotly_chart(fig, use_container_width=True)

    if tab_strategy:
        with tab_strategy:
            st.header("Custom Strategy Builder")
            st.write("Construct your own technical analysis strategy visually, and instantly backtest it against historical data!")
    
            st.subheader("Define Your Buy Rule")
            st.write("The strategy will automatically sell when the condition is false.")
    
            col1, col2, col3 = st.columns(3)
            indicator_map = {
                "Relative Strength Index (RSI)": "rsi_14",
                "Closing Price": "close",
                "20-Day Simple Moving Avg (SMA)": "sma_20",
                "50-Day Simple Moving Avg (SMA)": "sma_50",
                "MACD Line": "macd",
                "MACD Signal Line": "macd_signal"
            }
            metric_label = col1.selectbox("Indicator", list(indicator_map.keys()))
            metric = indicator_map[metric_label]
            operator = col2.selectbox("Operator", ["<", ">", "<=", ">=", "=="])
            threshold = col3.number_input("Threshold Value", value=30.0)
    
            if st.button("Run Custom Strategy", type="primary"):
                with st.spinner("Backtesting custom ruleset..."):
                    df_strat = get_stock_data(symbol_input, period=period)
                    if df_strat is not None and not df_strat.empty:
                        df_strat_enc = apply_indicators(df_strat)
                        if df_strat_enc is not None:
                            res_strat = run_custom_strategy(df_strat_enc, metric, operator, threshold)
                            if res_strat is None:
                                st.error("Strategy execution failed. Make sure the indicator exists and data is sufficient.")
                            else:
                                sum_strat = res_strat["summary"]
                                st.markdown("### Backtest Results")
                                sc1, sc2, sc3, sc4 = st.columns(4)
                                sc1.metric("Total Return", f"{sum_strat['total_return_pct']:.2f}%")
                                sc2.metric("Win Rate", f"{sum_strat['win_rate_pct']:.2f}%")
                                sc3.metric("Max Drawdown", f"{sum_strat['max_drawdown_pct']:.2f}%")
                                sc4.metric("Trades Executed", str(sum_strat["num_closed_trades"]))
                        
                                bt_frame = res_strat["backtest_frame"]
                                import plotly.graph_objects as go
                        
                                fig_strat = go.Figure()
                                fig_strat.add_trace(go.Candlestick(
                                    x=bt_frame.index,
                                    open=bt_frame['open'], high=bt_frame['high'],
                                    low=bt_frame['low'], close=bt_frame['close'],
                                    name='Price'
                                ))
                        
                                # Add Buy markers
                                buys = bt_frame[bt_frame["signal"] == 1]
                                if not buys.empty:
                                    fig_strat.add_trace(go.Scatter(
                                        x=buys.index,
                                        y=buys['low'] * 0.98,
                                        mode='markers',
                                        marker=dict(symbol='triangle-up', size=12, color='green', line=dict(width=2, color='DarkSlateGrey')),
                                        name='Buy Signal'
                                    ))
                        
                                fig_strat.update_layout(title=f"Custom Strategy: {metric.upper()} {operator} {threshold}", xaxis_title="Date", yaxis_title="Price", xaxis_rangeslider_visible=False, height=500)
                                st.plotly_chart(fig_strat, use_container_width=True)

    if tab_admin:
        with tab_admin:
            st.header("Admin Dashboard")
            st.write("Comprehensive platform management and user analytics.")
            users = get_all_users()
            if users:
                admin_t1, admin_t2 = st.tabs(["Registered Users", "User Portfolios & Analytics"])
        
                with admin_t1:
                    st.subheader("User Database")
                    df_users = pd.DataFrame(users)
                    df_users.rename(columns={
                        "id": "User ID", "username": "Username", "email": "Email Address",
                        "role": "Account Type", "created_at": "Registration Date"
                    }, inplace=True)
                    st.dataframe(df_users, use_container_width=True, hide_index=True)
            
                    st.subheader("Remove User")
                    with st.form("delete_user_form"):
                        del_id = st.number_input("Enter User ID to Delete (Admins cannot be deleted)", min_value=1, step=1)
                        del_submit = st.form_submit_button("Delete User", type="primary")
                        if del_submit:
                            target_user = next((u for u in users if u["id"] == del_id), None)
                            if not target_user:
                                st.error("User ID not found.")
                            elif target_user["role"] == "admin":
                                st.error("Cannot delete an admin account.")
                            else:
                                if delete_user(del_id):
                                    st.success(f"User {del_id} deleted successfully.")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete user from database.")
                            
                with admin_t2:
                    st.subheader("Portfolio Inspector")
                    st.write("Select any user below to view their active holdings and P&L.")
                    user_options = {f"ID: {u['id']} | {u['username']}": u["id"] for u in users}
                    selected_user_str = st.selectbox("Select User", list(user_options.keys()))
                    inspect_user_id = user_options[selected_user_str]
            
                    # Fetch their specific portfolio
                    user_summary = get_portfolio_value(inspect_user_id)
                    u_positions = user_summary["positions"]
            
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Total Cost", f"₹{user_summary['total_cost']:.2f}")
                    val = user_summary['total_market_value']
                    c2.metric("Total Market Value", "N/A" if val is None else f"₹{val:.2f}")
                    pnl = user_summary['total_pnl']
                    c3.metric("Total P&L", "N/A" if pnl is None else f"₹{pnl:.2f}")
            
                    st.write("**Current Holdings:**")
                    if u_positions:
                        df_u_pos = pd.DataFrame(u_positions)
                        df_u_pos.rename(columns={
                            "id": "Trade ID", "symbol": "Ticker", "qty": "Shares",
                            "avg_price": "Avg Buy Price", "total_cost": "Total Invested",
                            "market_value": "Current Value", "pnl": "Profit/Loss", "pnl_pct": "Return (%)"
                        }, inplace=True)
                        st.dataframe(df_u_pos, use_container_width=True, hide_index=True)
                    else:
                        st.info("This user currently has no open positions in their portfolio.")

elif st.session_state["current_page"] == "profile":
    st.title("My Profile")
    st.divider()
    summary = get_portfolio_value(st.session_state["user_id"])
    port_value = summary.get("total_market_value")
    port_value = float(port_value) if port_value is not None else 0.0
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Username", st.session_state.get("username", "Unknown"))
        st.metric("Email Address", st.session_state.get("email", "N/A"))
    with col2:
        st.metric("Total Portfolio Value", f"₹{port_value:,.2f}")
        st.metric("Trading Tier", "Elite" if port_value > 100000 else "Standard")

    st.divider()
    st.subheader("Profile Picture")
    c1, c2 = st.columns([1, 2])
    with c1:
        if st.session_state.get("profile_pic"):
            st.markdown(f'<img src="data:image/png;base64,{st.session_state["profile_pic"]}" style="width:150px;height:150px;border-radius:50%;object-fit:cover;box-shadow:0 4px 6px rgba(0,0,0,0.1);border:3px solid var(--accent-color);">', unsafe_allow_html=True)
            st.write("")
            if st.button("Remove Picture", type="secondary", use_container_width=True):
                from src.portfolio_manager import update_profile_picture
                update_profile_picture(st.session_state["user_id"], None)
                st.session_state["profile_pic"] = None
                st.rerun()
        else:
            st.markdown(f"""
            <div style="width: 150px; height: 150px; border-radius: 50%; background: linear-gradient(135deg, var(--accent-color), #3b82f6); color: white; display: flex; justify-content: center; align-items: center; font-size: 4rem; font-weight: 700; flex-shrink: 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                {st.session_state.get('username', 'U')[0].upper()}
            </div>
            """, unsafe_allow_html=True)
            
    with c2:
        uploaded_file = st.file_uploader("Upload a new profile picture", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            if st.button("Save Picture", type="primary"):
                try:
                    from PIL import Image
                    import io
                    import base64
                    from src.portfolio_manager import update_profile_picture
                    
                    img = Image.open(uploaded_file)
                    if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                    width, height = img.size
                    min_dim = min(width, height)
                    left = (width - min_dim)/2
                    top = (height - min_dim)/2
                    right = (width + min_dim)/2
                    bottom = (height + min_dim)/2
                    img = img.crop((left, top, right, bottom))
                    img = img.resize((200, 200), Image.Resampling.LANCZOS)
                    
                    buffered = io.BytesIO()
                    img.save(buffered, format="JPEG", optimize=True, quality=85)
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    
                    update_profile_picture(st.session_state["user_id"], img_str)
                    st.session_state["profile_pic"] = img_str
                    st.success("Profile picture updated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to process image: {e}")

elif st.session_state["current_page"] == "settings":
    st.title("App Settings")
    st.divider()
    st.subheader("Personalization")
    theme_choices = [
        "Midnight Pro (Dark)", "Cyberpunk (Dark)", "Deep Ocean (Dark)", 
        "Clean White (Light)", "Sunset Glow (Light)", "Mint Light (Light)"
    ]
    selected_theme = st.selectbox(
        "UI Theme", 
        theme_choices, 
        index=theme_choices.index(st.session_state.get("ui_theme", "Sunset Glow (Light)"))
    )
    if selected_theme != st.session_state.get("ui_theme"):
        st.session_state["ui_theme"] = selected_theme
        from src.portfolio_manager import update_user_theme
        update_user_theme(st.session_state["user_id"], selected_theme)
        st.rerun()
