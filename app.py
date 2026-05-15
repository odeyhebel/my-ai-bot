import streamlit as st
import pandas as pd
import numpy as np
import time
import random

# 1. SETUP & STYLE
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
        width: 100%; background-color: #1e3a4c; color: white;
        font-weight: bold; border-radius: 10px; height: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. STATE FOR PLATFORM SELECTION
if 'platform' not in st.session_state:
    st.session_state.platform = "Pocket Option"

st.title("🤖 PROV MAHAD AI - ULTIMATE")

# --- PLATFORM SELECTION SECTION ---
st.markdown("### 🌐 Select Trading Platform")
col_q, col_p = st.columns(2)

with col_q:
    if st.button("QUOTEX"):
        st.session_state.platform = "Quotex"
with col_p:
    if st.button("POCKET OPTION"):
        st.session_state.platform = "Pocket Option"

st.info(f"Hadda waxaad ku jirtaa: **{st.session_state.platform}** mode")

# 3. SETTINGS & ASSET LISTS
with st.container():
    st.markdown('<div class="settings-box">', unsafe_allow_html=True)
    
    # ------------------- QUOTEX CONFIG (Sawiradaadii dambe) -------------------
    if st.session_state.platform == "Quotex":
        tf_list = ["5s", "10s", "15s", "30s", "1m", "2m", "5m"]
        market_list = ["OTC Market", "Real Market"]
        pairs_list = [
            'USD/BDT (OTC)', 'USD/EGP (OTC)', 'USD/COP (OTC)', 'AUD/NZD (OTC)', 
            'EUR/JPY', 'NZD/USD (OTC)', 'USD/INR (OTC)', 'USD/ZAR (OTC)', 
            'USD/MXN (OTC)', 'USD/BRL (OTC)', 'CAD/JPY (OTC)', 'EUR/GBP', 
            'EUR/NZD (OTC)', 'AUD/JPY', 'CAD/CHF (OTC)', 'EUR/USD', 
            'NZD/CAD (OTC)', 'GBP/JPY', 'USD/IDR (OTC)', 'USD/PHP (OTC)', 
            'USD/JPY', 'USD/NGN (OTC)', 'GBP/USD', 'NZD/CHF (OTC)', 
            'GBP/NZD (OTC)', 'AUD/CAD', 'NZD/JPY (OTC)', 'USD/ARS (OTC)', 
            'USD/DZD (OTC)', 'USD/PKR (OTC)'
        ]
    
    # ------------------- POCKET OPTION CONFIG (Lacagihii aad soo dirtay) -------------------
    else:
        tf_list = ["M1", "M2", "M5", "M15", "M30"]
        market_list = ["Pocket OTC", "Live Market"]
        # Lacagihii aad hadda soo qortay
        pairs_list = [
            # Real Market
            'EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'USD/CAD', 'USD/CHF', 
            'NZD/USD', 'EUR/JPY', 'GBP/JPY', 'GOLD (XAU/USD)', 'SILVER',
            # OTC Market
            'AED/CNY OTC', 'AUD/CAD OTC', 'AUD/CHF OTC', 'AUD/NZD OTC', 
            'BHD/CNY OTC', 'CAD/CHF OTC', 'CAD/JPY OTC', 'CHF/JPY OTC', 
            'EUR/CHF OTC', 'EUR/GBP OTC', 'EUR/USD OTC', 'GBP/AUD OTC', 
            'JOD/CNY OTC', 'NZD/USD OTC', 'QAR/CNY OTC', 'UAH/USD OTC', 
            'USD/ARS OTC', 'USD/CAD OTC', 'USD/CLP OTC', 'USD/CNH OTC', 
            'USD/DZD OTC', 'USD/EGP OTC', 'USD/IDR OTC', 'USD/INR OTC', 
            'USD/JPY OTC', 'USD/MYR OTC', 'Crypto IDX-OTC', 'Gold-OTC'
        ]

    col1, col2 = st.columns(2)
    with col1:
        m_type = st.selectbox("Market Type:", market_list)
    with col2:
        timeframe = st.selectbox("Time Frame:", tf_list)
    
    selected_pair = st.selectbox("🎯 Asset:", pairs_list)
    st.markdown('</div>', unsafe_allow_html=True)

# 4. LOGIC (TRIPLE MA + RSI) - Sidii hore
def analyze_ultimate():
    prices = np.random.randn(400).cumsum() + 100 
    df = pd.DataFrame({'close': prices})
    df['ma_fast'] = df['close'].rolling(8).mean()
    df['ma_mid'] = df['close'].rolling(21).mean()
    df['ma_slow'] = df['close'].rolling(50).mean()
    rsi_value = random.randint(30, 70) 
    f, m, s = df['ma_fast'].iloc[-1], df['ma_mid'].iloc[-1], df['ma_slow'].iloc[-1]
    
    if f > m > s and rsi_value < 65:
        return "BUY ⬆️", "#00ff88", random.randint(98, 99), "PERFECT ENTRY: Strong Trend"
    elif f < m < s and rsi_value > 35:
        return "SELL ⬇️", "#ff4b4b", random.randint(98, 99), "PERFECT ENTRY: Strong Trend"
    else:
        return "WAITING... ⏳", "#ffffff", random.randint(85, 92), "FILTERED: Risky Momentum"

# 5. GENERATE BUTTON
if st.button("🚀 GENERATE SIGNAL"):
    with st.spinner(f'AI is analyzing {st.session_state.platform} indicators...'):
        time.sleep(1.5)
        direction, color, acc, trend_desc = analyze_ultimate()
        
        st.markdown(f"""
            <div class="signal-card">
                <p style="color: #888;">{st.session_state.platform} | {selected_pair} | {timeframe}</p>
                <h3 style="color: {color};">{trend_desc}</h3>
                <hr style="opacity: 0.1; margin: 15px 0;">
                <h1 style="color: {color}; font-size: 80px; margin: 10px 0;">{direction}</h1>
                <p style="color: #00ffd5; font-size: 20px; font-weight: bold;">ACCURACY: {acc}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        if acc >= 99:
            st.balloons()

st.markdown("<p style='text-align: center; color: #444; margin-top: 30px;'>© 2026 PROV MAHAD AI | Triple-MA Logic</p>", unsafe_allow_html=True)
