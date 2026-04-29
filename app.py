import streamlit as st
import pandas as pd
import numpy as np
import datetime
from streamlit_autorefresh import st_autorefresh

# 1. AUTO REFRESH - Waxaan ka dhignay 2 ilbiriqsi si uusan signal 5s ah kuugu dhaafin
st_autorefresh(interval=2000, key="focus_refresh")

# --- CONFIGURATION ---
st.set_page_config(page_title="Focused Trading Bot", layout="centered")
st.title("🎯 Precision Trading Bot")

# --- SIDEBAR: FOCUS SETTINGS ---
st.sidebar.header("Focus Mode Settings")
market_type = st.sidebar.radio("Market:", ["Real Market", "OTC Market"])

# Liiska Pairs-ka
REAL_PAIRS = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'EUR/GBP', 'USD/CAD', 'NZD/USD']
OTC_PAIRS = ['EUR/USD-OTC', 'GBP/USD-OTC', 'USD/JPY-OTC', 'AUD/USD-OTC', 'EUR/GBP-OTC', 
             'USD/CHF-OTC', 'NZD/USD-OTC', 'USD/CAD-OTC', 'EUR/JPY-OTC', 'GBP/JPY-OTC']

all_options = REAL_PAIRS if market_type == "Real Market" else OTC_PAIRS

# --- Halkan ayaad ka dooranaysaa hal Pair oo kaliya ---
selected_pair = st.sidebar.selectbox("🎯 Dooro hal Pair oo aad xoogga saarto:", all_options)
timeframe = st.sidebar.selectbox("Timeframe:", ["5s", "15s", "30s", "1m", "5m"])

# --- CORE LOGIC ---
def analyze_focused_pair(df):
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
    
    # Shuruudaha Signal-ka
    if last['ma_fast'] > last['ma_mid'] and last['rsi'] < 48 and last['k_line'] > last['d_line']:
        return "🔥 BUY NOW", "success"
    elif last['ma_fast'] < last['ma_mid'] and last['rsi'] > 52 and last['k_line'] < last['d_line']:
        return "📉 SELL NOW", "error"
    return "⏳ WAITING FOR PERFECT ENTRY", "info"

# --- DISPLAY ---
st.markdown(f"## 💎 Analyzing: {selected_pair}")
st.write(f"Focus Mode: Bot-ku wuxuu hadda si gaar ah u eegayaa **{selected_pair}** oo kaliya.")

# Simulating data
data = pd.DataFrame({
    'close': np.random.randn(100).cumsum() + 100,
    'low': np.random.randn(100).cumsum() + 98,
    'high': np.random.randn(100).cumsum() + 102
})

signal, status = analyze_focused_pair(data)

# Big Visual Signal (Si aadan u seegin)
st.divider()
if status == "success":
    st.button(f" {signal} ", use_container_width=True, type="primary")
    st.balloons() # Muuqaal farxad leh markuu Buy yimaado
elif status == "error":
    st.button(f" {signal} ", use_container_width=True)
else:
    st.info(f" {signal} ")

st.divider()
st.caption(f"Last scanned at: {datetime.datetime.now().strftime('%H:%M:%S')}")
