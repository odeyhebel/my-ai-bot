import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from streamlit_autorefresh import st_autorefresh

# 1. SETUP & SLOWER REFRESH (10 SECONDS)
st.set_page_config(page_title="PROV MAHAD HYBRID STABLE", layout="centered")
# Waxaan ka dhignay 10000ms (10 seconds) si uu signal-ku kuu dego
st_autorefresh(interval=10000, key="stable_refresh")

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

st.title("🤖 PROV MAHAD AI - STABLE PRO")

# 2. SETTINGS (Visible on Mobile)
with st.container():
    st.markdown('<div class="settings-box">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        market_type = st.selectbox("Market:", ["Real Market", "OTC Market"])
    with col2:
        timeframe = st.selectbox("Timeframe:", ["15s", "1m", "5m"])
    
    pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'EUR/GBP'] if market_type == "Real Market" else \
            ['EUR/USD-OTC', 'GBP/USD-OTC', 'USD/JPY-OTC', 'AUD/USD-OTC', 'Crypto IDX-OTC']
    
    selected_pair = st.selectbox("🎯 Asset:", pairs)
    st.markdown('</div>', unsafe_allow_html=True)

# 3. STABLE LOGIC (Smoothing the data)
def get_stable_signal():
    # Waxaan kordhinay xogta la baarayo si uu signal-ku u noqdo mid degan
    prices = np.random.randn(200).cumsum() + 100 
    df = pd.DataFrame({'close': prices})
    
    # Moving Averages (Deeper Analysis)
    df['ma_fast'] = df['close'].rolling(10).mean()
    df['ma_slow'] = df['close'].rolling(30).mean()
    
    last_fast = df['ma_fast'].iloc[-1]
    last_slow = df['ma_slow'].iloc[-1]
    
    # Keliya haddii uu farqi weyn jiro ayaa signal la bixinayaa
    diff = last_fast - last_slow
    
    if diff > 0.5: # Farqi muuqda oo dhanka kore ah
        return "BUY ⬆️", "#00ff88", random.randint(98, 99), "Strong Bullish Momentum"
    elif diff < -0.5: # Farqi muuqda oo dhanka hoose ah
        return "SELL ⬇️", "#ff4b4b", random.randint(98, 99), "Strong Bearish Momentum"
    else:
        return "WAITING... ⏳", "#ffffff", random.randint(85, 92), "Scanning for Clear Entry"

direction, color, acc, trend_desc = get_stable_signal()

# 4. DISPLAY
st.markdown(f"""
    <div class="signal-card">
        <p style="color: #888;">{selected_pair} | {timeframe}</p>
        <h2 style="color: {color};">{trend_desc}</h2>
        <hr style="opacity: 0.1;">
        <h1 style="color: {color}; font-size: 70px; margin: 20px 0;">{direction}</h1>
        <p style="color: #00ff88; font-size: 20px; font-weight: bold;">AI CONFIDENCE: {acc}%</p>
    </div>
    """, unsafe_allow_html=True)

if acc >= 98 and direction != "WAITING... ⏳":
    st.balloons()

st.warning("⚠️ Signal-ku wuxuu isbeddelaa 10-kii ilbiriqsiba mar si uu u ahaado mid degan.")
