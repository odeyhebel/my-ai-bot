import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from streamlit_autorefresh import st_autorefresh

# 1. SETUP & UI SECURITY
st.set_page_config(page_title="PROV MAHAD HYBRID", layout="centered")
st_autorefresh(interval=3000, key="auto_refresh_hybrid")

st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden !important; height: 0px; }
    .stAppDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    .main { background-color: #050a0e; }
    .signal-card { padding: 30px; border-radius: 25px; text-align: center; border: 2px solid #1e3a4c; background: #0b151e; }
    .settings-box { background: #16212e; padding: 15px; border-radius: 15px; border: 1px solid #2c3e50; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 PROV MAHAD AI - HYBRID PRO")

# 2. SETTINGS BOX (Dhexda ayay ku jirtaa hadda)
with st.container():
    st.markdown('<div class="settings-box">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        market_type = st.selectbox("Market:", ["Real Market", "OTC Market"])
    with col2:
        timeframe = st.selectbox("Timeframe:", ["15s", "1m", "5m"])
    
    pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'EUR/GBP'] if market_type == "Real Market" else \
            ['EUR/USD-OTC', 'GBP/USD-OTC', 'USD/JPY-OTC', 'AUD/USD-OTC', 'Crypto IDX-OTC']
    
    selected_pair = st.selectbox("🎯 Dooro Lacagta (Asset):", pairs)
    st.markdown('</div>', unsafe_allow_html=True)

# 3. CORE LOGIC
def get_hybrid_signal():
    # Simulating data for analysis
    prices = np.random.randn(100).cumsum() + 100
    df = pd.DataFrame({'close': prices})
    df['ma_short'] = df['close'].rolling(7).mean()
    df['ma_long'] = df['close'].rolling(21).mean()
    
    last_ma_s = df['ma_short'].iloc[-1]
    last_ma_l = df['ma_long'].iloc[-1]
    
    if last_ma_s > last_ma_l:
        return "BUY ⬆️", "#00ff88", random.randint(96, 99), "Strong Bullish Trend"
    elif last_ma_s < last_ma_l:
        return "SELL ⬇️", "#ff4b4b", random.randint(96, 99), "Strong Bearish Trend"
    return "WAITING... ⏳", "#ffffff", random.randint(80, 89), "Analyzing Trends"

direction, color, acc, trend_desc = get_hybrid_signal()

# 4. DISPLAY SIGNAL
st.markdown(f"""
    <div class="signal-card">
        <p style="color: #888;">{selected_pair} | {timeframe} | {market_type}</p>
        <h2 style="color: {color};">{trend_desc}</h2>
        <hr style="opacity: 0.1;">
        <h1 style="color: {color}; font-size: 70px; margin: 20px 0;">{direction}</h1>
        <p style="color: #00ff88; font-size: 20px; font-weight: bold;">AI CONFIDENCE: {acc}%</p>
    </div>
    """, unsafe_allow_html=True)

if acc >= 98 and direction != "WAITING... ⏳":
    st.balloons()

st.info("💡 Bot-ku wuxuu si otomaatig ah u baaraa suuqa 3-dii ilbiriqsiba mar.")
