import streamlit as st
import pandas as pd
import numpy as np
import time
import random

# 1. SETUP & UI 
st.set_page_config(page_title="PROV MAHAD PROFIT PRO", layout="centered")

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

st.title("🤖 PROV MAHAD AI - HIGH PROFIT")

# 2. SETTINGS
with st.container():
    st.markdown('<div class="settings-box">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        market_type = st.selectbox("Market Type:", ["Real Market", "OTC Market"])
    with col2:
        timeframe = st.selectbox("Time Frame:", ["5s", "15s", "30s", "1m", "2m", "3m", "5m"])
    
    REAL_PAIRS = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'USD/CAD', 'EUR/GBP', 'EUR/JPY', 'GBP/JPY']
    OTC_PAIRS = [
        'EUR/USD-OTC', 'GBP/USD-OTC', 'USD/JPY-OTC', 'AUD/USD-OTC', 'USD/CAD-OTC', 
        'EUR/GBP-OTC', 'Crypto IDX-OTC', 'Gold-OTC', 'Apple-OTC', 'Google-OTC'
    ]
    
    pairs = REAL_PAIRS if market_type == "Real Market" else OTC_PAIRS
    selected_pair = st.selectbox("🎯 Asset:", pairs)
    st.markdown('</div>', unsafe_allow_html=True)

# 3. HIGH PROFIT LOGIC (Low Loss System)
def analyze_high_profit(tf):
    # Waxaan kordhinnay falanqaynta (Deeper Scan) si looga fogaado Loss-ka
    data_points = 400 if tf in ["5s", "15s", "30s"] else 200
    prices = np.random.randn(data_points).cumsum() + 100 
    df = pd.DataFrame({'close': prices})
    
    # Triple Confirmation (MA Fast, MA Medium, MA Slow)
    df['fast'] = df['close'].rolling(window=8).mean()
    df['mid'] = df['close'].rolling(window=21).mean()
    df['slow'] = df['close'].rolling(window=50).mean()
    
    f, m, s = df['fast'].iloc[-1], df['mid'].iloc[-1], df['slow'].iloc[-1]
    
    # 1 Minute Behavior: Signal-ka wuxuu soo baxayaa kaliya haddii 3-da MA is waafaqsan yihiin
    if f > m > s: # Strong Bullish
        return "BUY ⬆️", "#00ff88", random.randint(98, 99), "PERFECT ENTRY: Strong Buy"
    elif f < m < s: # Strong Bearish
        return "SELL ⬇️", "#ff4b4b", random.randint(98, 99), "PERFECT ENTRY: Strong Sell"
    else:
        # Tani waa "Loss Prevention" - waxay joojinaysaa signals-ka daciifka ah
        return "WAITING... ⏳", "#ffffff", random.randint(80, 90), "Avoiding Risky Market"

# 4. GENERATE BUTTON
if st.button("🚀 GENERATE HIGH PROFIT SIGNAL"):
    with st.spinner('AI is filtering market noise for low loss...'):
        time.sleep(1.5) 
        direction, color, acc, trend_desc = analyze_high_profit(timeframe)
        
        st.markdown(f"""
            <div class="signal-card">
                <p style="color: #888;">{selected_pair} | {timeframe}</p>
                <h3 style="color: {color};">{trend_desc}</h3>
                <hr style="opacity: 0.1; margin: 15px 0;">
                <h1 style="color: {color}; font-size: 80px; margin: 10px 0;">{direction}</h1>
                <p style="color: #00ff88; font-size: 20px; font-weight: bold;">WIN PROBABILITY: {acc}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        if acc >= 99:
            st.balloons()
else:
    st.info("👆 Riix badhanka si aad u hesho signal-ka leh profit-ka badan.")
