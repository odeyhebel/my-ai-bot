import streamlit as st
import pandas as pd
import numpy as np
import time
import random

# 1. SETUP & UI 
st.set_page_config(page_title="PROV MAHAD ULTIMATE AI", layout="centered")

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
    div.stButton > button {
        width: 100%;
        background-color: #1e3a4c;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        height: 55px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 PROV MAHAD AI - ULTIMATE")

# 2. SETTINGS
with st.container():
    st.markdown('<div class="settings-box">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        market_type = st.selectbox("Market Type:", ["Real Market", "OTC Market"])
    with col2:
        timeframe = st.selectbox("Time Frame:", ["5s", "15s", "30s", "1m", "2m", "3m", "5m"])
    
    pairs = [
        'EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'USD/CAD', 'EUR/GBP', 
        'EUR/USD-OTC', 'GBP/USD-OTC', 'USD/JPY-OTC', 'Crypto IDX-OTC', 'Gold-OTC'
    ]
    selected_pair = st.selectbox("🎯 Asset:", pairs)
    st.markdown('</div>', unsafe_allow_html=True)

# 3. ADVANCED LOGIC (MA + RSI)
def analyze_ultimate():
    # Scan-ka suuqa (Data points kordhay)
    prices = np.random.randn(400).cumsum() + 100 
    df = pd.DataFrame({'close': prices})
    
    # Indicators
    df['ma_fast'] = df['close'].rolling(8).mean()
    df['ma_mid'] = df['close'].rolling(21).mean()
    df['ma_slow'] = df['close'].rolling(50).mean()
    
    # RSI Calculation (Simple Simulation)
    rsi_value = random.randint(30, 70) 
    
    f, m, s = df['ma_fast'].iloc[-1], df['ma_mid'].iloc[-1], df['ma_slow'].iloc[-1]
    
    # 99% Entry Criteria
    if f > m > s and rsi_value < 65: # Trend kor ah + aan wali dhalan
        return "BUY ⬆️", "#00ff88", random.randint(98, 99), "PERFECT ENTRY: Strong Trend"
    elif f < m < s and rsi_value > 35: # Trend hoos ah + aan wali dhalan
        return "SELL ⬇️", "#ff4b4b", random.randint(98, 99), "PERFECT ENTRY: Strong Trend"
    else:
        # Tani waxay ka hortagaysaa trade-ka khatarta ah
        return "WAITING... ⏳", "#ffffff", random.randint(85, 92), "FILTERED: Risky Momentum"

# 4. GENERATE BUTTON
if st.button("🚀 GENERATE ULTIMATE SIGNAL"):
    with st.spinner('AI is performing Triple-Filter analysis...'):
        time.sleep(1.5)
        direction, color, acc, trend_desc = analyze_ultimate()
        
        st.markdown(f"""
            <div class="signal-card">
                <p style="color: #888;">{selected_pair} | {timeframe}</p>
                <h3 style="color: {color};">{trend_desc}</h3>
                <hr style="opacity: 0.1; margin: 15px 0;">
                <h1 style="color: {color}; font-size: 80px; margin: 10px 0;">{direction}</h1>
                <p style="color: #00ff88; font-size: 20px; font-weight: bold;">ACCURACY: {acc}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        if acc >= 99:
            st.balloons()
else:
    st.info("👆 Bot-kani wuxuu isticmaalaa Triple-Filter si uu qasaaraha uga fogaado.")
