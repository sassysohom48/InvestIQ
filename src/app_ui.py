from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.analysis_engine import (
    apply_indicators,
    calculate_position_size,
    generate_signal,
    predict_price,
)
from src.backtest import run_sma_crossover_backtest
from src.data_engine import get_stock_data
from src.portfolio_manager import add_trade, get_holdings, get_portfolio_value, remove_trade


st.set_page_config(page_title="OpenTrade Analytics", layout="wide")
st.title("OpenTrade Analytics")
st.caption("NSE-focused analytics dashboard (Phase 5 MVP)")


def _signal_color(signal: str) -> str:
    if signal == "BUY":
        return "green"
    if signal == "SELL":
        return "red"
    return "orange"


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


with st.sidebar:
    st.header("Controls")
    symbol_input = st.text_input("Stock Symbol (NSE)", value="RELIANCE")
    period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=1)
    risk_pct = st.slider("Risk % per trade", 0.5, 5.0, 2.0, 0.5)
    capital = st.number_input("Capital", min_value=1000.0, value=100000.0, step=1000.0)
    stop_loss_pct = st.slider("Stop Loss %", 1.0, 20.0, 5.0, 0.5)


tab_market, tab_backtest, tab_portfolio = st.tabs(["Market View", "Backtest", "Portfolio"])

with tab_market:
    df = get_stock_data(symbol_input, period=period)
    if df is None or df.empty:
        st.error("Could not fetch stock data. Please check the symbol and try again.")
    else:
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
            pred = predict_price(enriched, lookback=60, test_size=0.2)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Latest Close", f"{latest_close:.2f}")
            c2.markdown(
                f"### <span style='color:{_signal_color(signal)}'>Signal: {signal}</span>",
                unsafe_allow_html=True,
            )
            if pred is not None:
                c3.metric("Predicted Next Close", f"{pred['predicted_close']:.2f}")
                c4.metric("Model MAE", f"{pred['mae']:.2f} ({pred['mae_pct_of_price']:.2f}%)")
            else:
                c3.metric("Predicted Next Close", "N/A")
                c4.metric("Model MAE", "N/A")

            st.subheader("Position Sizing")
            s1, s2, s3 = st.columns(3)
            s1.metric("Risk Amount", f"{sizing['risk_amount']:.2f}")
            s2.metric("Suggested Shares", f"{int(sizing['shares'])}")
            s3.metric("Position Value", f"{sizing['position_value']:.2f}")

with tab_portfolio:
    st.subheader("Holdings")
    holdings = get_holdings()
    if holdings:
        st.dataframe(pd.DataFrame(holdings), use_container_width=True)
    else:
        st.info("No holdings yet.")

    st.subheader("Add Trade")
    with st.form("add_trade_form"):
        a_symbol = st.text_input("Symbol", value="RELIANCE", key="add_symbol")
        a_qty = st.number_input("Quantity", min_value=1, value=10, step=1, key="add_qty")
        a_price = st.number_input("Buy Price", min_value=0.01, value=1000.0, step=0.5, key="add_price")
        add_submit = st.form_submit_button("Add Trade")
        if add_submit:
            try:
                trade_id = add_trade(a_symbol, int(a_qty), float(a_price))
                st.success(f"Trade added with ID {trade_id}")
            except Exception as exc:
                st.error(f"Failed to add trade: {exc}")

    st.subheader("Remove Trade")
    with st.form("remove_trade_form"):
        r_trade_id = st.number_input("Trade ID", min_value=1, value=1, step=1)
        remove_submit = st.form_submit_button("Remove Trade")
        if remove_submit:
            ok = remove_trade(int(r_trade_id))
            if ok:
                st.success("Trade removed.")
            else:
                st.warning("Trade ID not found.")

    st.subheader("Portfolio Value")
    summary = get_portfolio_value()
    positions = summary["positions"]
    if positions:
        st.dataframe(pd.DataFrame(positions), use_container_width=True)
    st.metric("Total Cost", f"{summary['total_cost']:.2f}")
    st.metric(
        "Total Market Value",
        "N/A" if summary["total_market_value"] is None else f"{summary['total_market_value']:.2f}",
    )
    st.metric("Total P&L", "N/A" if summary["total_pnl"] is None else f"{summary['total_pnl']:.2f}")

with tab_backtest:
    st.subheader("SMA Crossover Backtest")
    st.caption("Strategy: Buy when SMA20 > SMA50, stay in cash otherwise.")

    bt_df = get_stock_data(symbol_input, period="2y")
    if bt_df is None or bt_df.empty:
        st.error("Could not fetch 2-year data for backtest.")
    else:
        bt_result = run_sma_crossover_backtest(bt_df, short_window=20, long_window=50)
        if bt_result is None:
            st.error("Could not run backtest on current data.")
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
                title=f"{symbol_input.upper()} Backtest Equity Curve",
                xaxis_title="Date",
                yaxis_title="Equity (start=1.0)",
                height=420,
            )
            st.plotly_chart(fig, use_container_width=True)
