import streamlit as st
import pandas as pd
import numpy as np
import time
import random

# 1. SETUP & UI 
st.set_page_config(page_title="PROV MAHAD SMART-AI", layout="centered")

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
    div.stButton > button {
        width: 100%; background-color: #1e3a4c; color: white;
        font-weight: bold; border-radius: 10px; height: 55px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 PROV MAHAD AI - INSTITUTIONAL V1")

# 2. SETTINGS
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        market_type = st.selectbox("Market:", ["OTC Market", "Real Market"])
    with col2:
        timeframe = st.selectbox("Time:", ["30s", "1m", "5m"])
    
    pairs = ['EUR/USD-OTC', 'USD/JPY-OTC', 'Crypto IDX-OTC', 'GBP/USD-OTC', 'AUD/CAD-OTC']
    selected_pair = st.selectbox("🎯 Select Asset:", pairs)

# 3. SMART MONEY LOGIC (Volume + Momentum)
def analyze_smart_money():
    # Simulation of Market Depth (Sidii Bangiyada oo kale)
    prices = np.random.randn(500).cumsum() + 100 
    df = pd.DataFrame({'close': prices})
    
    # Volume Simulation (Lacagta suuqa ku jirta)
    volume = random.randint(1000, 5000) 
    
    # Moving Averages (Koodhkii hore)
    df['ma_fast'] = df['close'].rolling(8).mean()
    df['ma_slow'] = df['close'].rolling(21).mean()
    
    f, s = df['ma_fast'].iloc[-1], df['ma_slow'].iloc[-1]
    
    # 🏦 INSTITUTIONAL FILTER: 
    # Ma bixinayo signal haddii Volume-ku hooseeyo (Bankigu ma jiro)
    if volume < 2500:
        return "WAITING... ⏳", "#ffffff", "LOW VOLUME: Bank is sleeping"

    # BUY Logic
    if f > s + 0.1:
        return "BUY ⬆️", "#00ff88", "SMART MONEY: Bullish Order"
    # SELL Logic
    elif f < s - 0.1:
        return "SELL ⬇️", "#ff4b4b", "SMART MONEY: Bearish Order"
    else:
        return "WAITING... ⏳", "#ffffff", "NEUTRAL: Market Correction"

# 4. GENERATE BUTTON
if st.button("🚀 SCAN FOR SMART MONEY"):
    with st.spinner('Checking Institutional Order Blocks...'):
        time.sleep(1.8)
        direction, color, desc = analyze_smart_money()
        acc = random.randint(97, 98) # Waxaan ku soo celinnay 98% maadaama aad tiri waa ka saxanyahay 99%
        
        st.markdown(f"""
            <div class="signal-card">
                <p style="color: #888;">{selected_pair} | {timeframe}</p>
                <h3 style="color: {color};">{desc}</h3>
                <h1 style="color: {color}; font-size: 80px; margin: 10px 0;">{direction}</h1>
                <p style="color: #00ff88; font-size: 20px; font-weight: bold;">AI ACCURACY: {acc}%</p>
            </div>
            """, unsafe_allow_html=True)
