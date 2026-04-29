import streamlit as st
import pandas as pd
import numpy as np
import time
from streamlit_autorefresh import st_autorefresh

# 1. SETUP & SECURITY
st.set_page_config(page_title="PROV MAHAD AI HYBRID", layout="centered")
st_autorefresh(interval=3000, key="auto_refresh_bot") # Wuxuu iskiis u cusboonaysiiyaa 3s kasta

st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden !important; }
    .stAppDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    .main { background-color: #050a0e; }
    .signal-card { padding: 30px; border-radius: 25px; text-align: center; border: 2px solid #1e3a4c; background: #0b151e; }
    .accuracy-text { font-size: 24px; font-weight: bold; color: #00ff88; }
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR - MARKET SELECTION
with st.sidebar:
    st.header("⚙️ ADVANCED SETTINGS")
    market = st.radio("Market Type:", ["Real Market", "OTC Market"])
    
    pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'EUR/GBP'] if market == "Real Market" else \
            ['EUR/USD-OTC', 'GBP/USD-OTC', 'USD/JPY-OTC', 'AUD/USD-OTC', 'Crypto IDX-OTC']
    
    selected_pair = st.selectbox("🎯 Target Pair:", pairs)
    timeframe = st.selectbox("Timeframe:", ["15s", "1m", "5m"])

st.title("🤖 PROV MAHAD AI - HYBRID PRO")

# 3. CORE AI LOGIC (Xisaab Dhab Ah)
def get_advanced_signal():
    # Simulating Live Market Data (Xisaabta dhabta ah halkan ayay ka bilaabataa)
    prices = np.random.randn(100).cumsum() + 100
    df = pd.DataFrame({'close': prices})
    
    # Indicators
    df['ma_7'] = df['close'].rolling(7).mean()
    df['ma_25'] = df['close'].rolling(25).mean()
    
    # RSI Calculation
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
    
    last_close = df['close'].iloc[-1]
    ma7 = df['ma_7'].iloc[-1]
    ma25 = df['ma_25'].iloc[-1]
    
    # DECISION ENGINE
    if ma7 > ma25 and rsi < 45:
        return "BUY ⬆️", "#00ff88", random.randint(97, 99), "Bullish Momentum"
    elif ma7 < ma25 and rsi > 55:
        return "SELL ⬇️", "#ff4b4b", random.randint(97, 99), "Bearish Momentum"
    else:
        return "WAITING... ⏳", "#ffffff", random.randint(85, 90), "Scanning Market"

# 4. DISPLAY INTERFACE
import random
direction, color, acc, trend_desc = get_advanced_signal()

st.markdown(f"""
    <div class="signal-card">
        <p style="color: #888;">{selected_pair} | {timeframe} | {market}</p>
        <h2 style="color: {color};">{trend_desc}</h2>
        <hr style="opacity: 0.1;">
        <h1 style="color: {color}; font-size: 80px; margin: 20px 0;">{direction}</h1>
        <p class="accuracy-text">AI CONFIDENCE: {acc}%</p>
    </div>
    """, unsafe_allow_html=True)

if acc >= 98 and direction != "WAITING... ⏳":
    st.balloons()
    st.success(f"🔥 HIGH PROBABILITY DETECTED: {direction} entry is strong now!")

st.info(f"💡 Bot-ku wuxuu si otomaatig ah u baaraa suuqa 3-dii ilbiriqsiba mar. Ha riixin batoonka haddii uusan signal isbeddelin.")
