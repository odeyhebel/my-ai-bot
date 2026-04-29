import streamlit as st
import pandas as pd
import numpy as np
import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Pro Trading Bot AI", layout="wide")
st.title("🤖 Pro-Level AI Trading Bot")

# --- SIDEBAR: SETTINGS ---
st.sidebar.header("Bot Settings")
market_type = st.sidebar.radio("Select Market:", ["Real Market", "OTC Market"])
timeframe = st.sidebar.selectbox("Select Timeframe:", ["5s", "15s", "30s", "1m", "2m", "3m", "5m"])

# Pairs lists
REAL_PAIRS = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'EUR/GBP', 'USD/CAD', 'NZD/USD']
OTC_PAIRS = ['EUR/USD-OTC', 'GBP/USD-OTC', 'USD/JPY-OTC', 'AUD/USD-OTC', 'EUR/GBP-OTC', 
             'USD/CHF-OTC', 'NZD/USD-OTC', 'USD/CAD-OTC', 'EUR/JPY-OTC', 'GBP/JPY-OTC']

selected_pairs = REAL_PAIRS if market_type == "Real Market" else OTC_PAIRS

# --- LOGIC FUNCTION ---
def analyze_data(df):
    # Moving Averages
    df['ma_fast'] = df['close'].rolling(7).mean()
    df['ma_mid'] = df['close'].rolling(14).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['rsi'] = 100 - (100 / (1 + (gain/loss)))

    # Stochastic
    low_min = df['low'].rolling(14).min()
    high_max = df['high'].rolling(14).max()
    df['k_line'] = 100 * ((df['close'] - low_min) / (high_max - low_min))
    df['d_line'] = df['k_line'].rolling(3).mean()
    
    last = df.iloc[-1]
    if last['ma_fast'] > last['ma_mid'] and last['rsi'] < 40 and last['k_line'] > last['d_line']:
        return "🔥 BUY SIGNAL", "success"
    elif last['ma_fast'] < last['ma_mid'] and last['rsi'] > 60 and last['k_line'] < last['d_line']:
        return "📉 SELL SIGNAL", "error"
    return "⏳ WAITING", "info"

# --- MAIN DASHBOARD ---
st.subheader(f"Scanning: {market_type} ({len(selected_pairs)} Pairs)")

cols = st.columns(3) # Display pairs in 3 columns

for i, pair in enumerate(selected_pairs):
    # Tusaale xog ah (In real life, halkan API ayaa xogta ka keeni lahaa)
    data = pd.DataFrame({
        'close': np.random.randn(50).cumsum() + 100,
        'low': np.random.randn(50).cumsum() + 95,
        'high': np.random.randn(50).cumsum() + 105
    })
    
    signal, status = analyze_data(data)
    
    with cols[i % 3]:
        st.info(f"**{pair}**")
        if status == "success": st.success(signal)
        elif status == "error": st.error(signal)
        else: st.warning(signal)

st.divider()
st.write(f"Last Update: {datetime.datetime.now().strftime('%H:%M:%S')}")
