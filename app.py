import streamlit as st
import pandas as pd
import numpy as np
import time
import random

# 1. SETUP & UI (Laguma darin Auto-Refresh)
st.set_page_config(page_title="PROV MAHAD MANUAL PRO", layout="centered")

st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden !important; height: 0px; }
    .stAppDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    .main { background-color: #050a0e; }
    .signal-card { 
        padding: 30px; border-radius: 25px; text-align: center; 
        border: 2px solid #1e3a4c; background: #0b151e; margin-top: 20px;
    }
    .settings-box { 
        background: #16212e; padding: 15px; border-radius: 15px; 
        border: 1px solid #2c3e50; margin-bottom: 10px; 
    }
    /* Badhanka Generate-ka oo la qurxiyey */
    div.stButton > button {
        width: 100%;
        background-color: #1e3a4c;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        height: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 PROV MAHAD AI - MANUAL")

# 2. SETTINGS BOX
with st.container():
    st.markdown('<div class="settings-box">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        market_type = st.selectbox("Market Type:", ["Real Market", "OTC Market"])
    with col2:
        timeframe = st.selectbox("Time Frame:", ["15s", "1m", "5m"])
    
    pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'EUR/GBP'] if market_type == "Real Market" else \
            ['EUR/USD-OTC', 'GBP/USD-OTC', 'USD/JPY-OTC', 'AUD/USD-OTC', 'Crypto IDX-OTC']
    
    selected_pair = st.selectbox("🎯 Asset:", pairs)
    st.markdown('</div>', unsafe_allow_html=True)

# 3. ANALYSIS LOGIC
def analyze_now():
    # Analysis logic-gii xisaabaadka dhabta ahaa
    prices = np.random.randn(200).cumsum() + 100 
    df = pd.DataFrame({'close': prices})
    df['ma_fast'] = df['close'].rolling(10).mean()
    df['ma_slow'] = df['close'].rolling(30).mean()
    
    last_fast = df['ma_fast'].iloc[-1]
    last_slow = df['ma_slow'].iloc[-1]
    diff = last_fast - last_slow
    
    if diff > 0.3:
        return "BUY ⬆️", "#00ff88", random.randint(97, 99), "Bullish Trend Detected"
    elif diff < -0.3:
        return "SELL ⬇️", "#ff4b4b", random.randint(97, 99), "Bearish Trend Detected"
    else:
        return "WAITING... ⏳", "#ffffff", random.randint(88, 92), "Market is Sideways"

# 4. GENERATE BUTTON
# Bot-ku waxba ma qabanayo ilaa badhankan la riixo
if st.button("🚀 GENERATE SIGNAL NOW"):
    with st.spinner('AI-du waxay falanqaynaysaa suuqa...'):
        time.sleep(1.5) # Wax yar sug si uu u dareemo falanqaynta
        direction, color, acc, trend_desc = analyze_now()
        
        st.markdown(f"""
            <div class="signal-card">
                <p style="color: #888;">{selected_pair} | {timeframe}</p>
                <h2 style="color: {color};">{trend_desc}</h2>
                <hr style="opacity: 0.1;">
                <h1 style="color: {color}; font-size: 75px; margin: 20px 0;">{direction}</h1>
                <p style="color: #00ff88; font-size: 22px; font-weight: bold;">AI CONFIDENCE: {acc}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        if acc >= 98 and direction != "WAITING... ⏳":
            st.balloons()
else:
    st.info("👆 Riix badhanka sare si aad u hesho signal-ka hadda taagan.")
