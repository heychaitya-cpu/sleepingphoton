import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="StockPulse Pro", layout="wide")

# Initialize Session State for Watchlist & Alerts
if "watchlist" not in st.session_state:
    st.session_state.watchlist = [
        {"ticker": "RELIANCE.NS", "target_buy": 2800.0},
        {"ticker": "TCS.NS", "target_buy": 3900.0},
        {"ticker": "INFY.NS", "target_buy": 1750.0},
        {"ticker": "AAPL", "target_buy": 210.0}
    ]

# Helper: Calculate RSI
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Helper: Fetch Stock Metrics & Verdict
@st.cache_data(ttl=300)
def analyze_stock(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)
    info = stock.info
    hist = stock.history(period="1y")
    
    if hist.empty:
        return None

    current_price = hist["Close"].iloc[-1]
    sma_50 = hist["Close"].rolling(50).mean().iloc[-1]
    sma_200 = hist["Close"].rolling(200).mean().iloc[-1]
    rsi = compute_rsi(hist["Close"]).iloc[-1]

    pe_ratio = info.get("trailingPE", np.nan)
    roe = info.get("returnOnEquity", 0) * 100 if info.get("returnOnEquity") else np.nan
    debt_to_eq = info.get("debtToEquity", np.nan)
    rev_growth = info.get("revenueGrowth", 0) * 100 if info.get("revenueGrowth") else np.nan

    # Automated Scoring Engine (Buy / Hold / Avoid Verdict)
    score = 0
    reasons = []

    if not np.isnan(pe_ratio) and 0 < pe_ratio < 25:
        score += 2
        reasons.append(f"Attractive P/E valuation ({pe_ratio:.1f})")
    elif not np.isnan(pe_ratio) and pe_ratio >= 50:
        score -= 1
        reasons.append(f"High P/E valuation ({pe_ratio:.1f})")
