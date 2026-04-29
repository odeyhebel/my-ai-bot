import streamlit as st
import pandas as pd
import numpy as np
import datetime

# 1. AUTO REFRESH - Bot-ka ayaa is cusboonaysiinaya 10-kii ilbiriqsiba
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10000, key="bot_refresh")

# --- CONFIGURATION ---
st.set_page_config(page_title="Pro-Level AI Trading Bot", layout="wide")
st.title("🤖 Pro-Level AI Trading Bot")

# --- SIDEBAR: SETTINGS ---
st.sidebar.header("Bot Control Panel")
market_type = st.sidebar.radio("Select Market Type:", ["Real Market", "OTC Market"])
timeframe = st.sidebar.selectbox("Select Timeframe:", ["5s", "15s", "30s", "1m", "2m", "3m", "5m"])

# Pairs lists
REAL_PAIRS = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'EUR/GBP', 'USD/CAD', 'NZD/USD']
OTC_PAIRS = ['EUR/USD-OTC', 'GBP/USD-OTC', 'USD/JPY-OTC', 'AUD/USD-OTC', 'EUR/GBP-OTC', 
             'USD/CHF-OTC', 'NZD/USD-OTC', 'USD/CAD-OTC', 'EUR/JPY-OTC', 'GBP/JPY-OTC']

selected_pairs = REAL_PAIRS if market_type == "Real Market" else OTC_PAIRS

# --- CORE LOGIC FUNCTION ---
def analyze_strategy(df):
    # Moving Averages
    df['ma_fast'] = df['close'].rolling(window=7).mean()   
    df['ma_mid'] = df['close'].rolling(window=14).mean()   
    
    # RSI (14)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['rsi'] = 100 - (100 / (1 + (gain/loss)))

    # Stochastic Oscillator
    low_min = df['low'].rolling(window=14).min()
    high_max = df['high'].rolling(window=14).max()
    df['k_line'] = 100 * ((df['close'] - low_min) / (high_max - low_min))
    df['d_line'] = df['k_line'].rolling(window=3).mean()

    last = df.iloc[-1]
    
    # Pro Signals (RSI & MA & Stochastic)
    if (last['ma_fast'] > last['ma_mid']) and (last['rsi'] < 45) and (last['k_line'] > last['d_line']):
        return "🚀 BUY SIGNAL", "success"
    elif (last['ma_fast'] < last['ma_mid']) and (last['rsi'] > 55) and (last['k_line'] < last['d_line']):
        return "📉 SELL SIGNAL", "error"
    
    return "⏳ WAITING", "info"

# --- MAIN DASHBOARD ---
st.subheader(f"Status: Scanning {market_type} ({len(selected_pairs)} Pairs)")

cols = st.columns(2) # Laba lammaane hal saf (Double column layout)

for i, pair in enumerate(selected_pairs):
    # Simulating Live Data (Halkan waxaa imaan doona API-gaaga mustaqbalka)
    data = pd.DataFrame({
        'close': np.random.randn(100).cumsum() + 100,
        'low': np.random.randn(100).cumsum() + 98,
        'high': np.random.randn(100).cumsum() + 102
    })
    
    signal, status = analyze_strategy(data)
    
    with cols[i % 2]:
        with st.container():
            st.markdown(f"### {pair}")
            if status == "success":
                st.success(f"**{signal}** | TF: {timeframe}")
            elif status == "error":
                st.error(f"**{signal}** | TF: {timeframe}")
            else:
                st.info(f"**{signal}**")

st.divider()
st.write(f"Cusboonaysiintii u dambeysay: {datetime.datetime.now().strftime('%H:%M:%S')} | GMT+3")
