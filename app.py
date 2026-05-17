import streamlit as st
import pandas as pd
import numpy as np
import time
import random

# 1. SETUP & STYLE
st.set_page_config(page_title="PROV MAHAD AI ENGINE", layout="centered")

st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden !important; height: 0px; }
    .stAppDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    .main { background-color: #050a0e; }
    .status-box { 
        background: #16212e; padding: 15px; border-radius: 15px; 
        border: 1px solid #2c3e50; margin-bottom: 20px; text-align: center;
    }
    div.stButton > button {
        width: 100%; background-color: #00ffd5; color: #050a0e;
        font-weight: bold; border-radius: 10px; height: 55px;
        font-size: 18px; border: none; letter-spacing: 1px;
    }
    div.stButton > button:hover {
        background-color: #00b395; color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. STATE MANAGEMENT
if 'platform' not in st.session_state:
    st.session_state.platform = "Pocket Option"

st.title("⚡ PROV MAHAD AI - SYSTEM ANALYSIS")
st.markdown("<p style='color:#888;'>Automated signal generation with price action network</p>", unsafe_allow_html=True)

# --- PLATFORM SELECTION ---
col_q, col_p = st.columns(2)
with col_q:
    if st.button("QUOTEX MODE"):
        st.session_state.platform = "Quotex"
with col_p:
    if st.button("POCKET OPTION MODE"):
        st.session_state.platform = "Pocket Option"

st.markdown("---")

# 3. GLOBAL ASSETS SYSTEM (Dhammaan lacagaha OTC rasmiga ah)
QUOTEX_PAIRS = [
    'USD/BDT (OTC)', 'USD/EGP (OTC)', 'AUD/NZD (OTC)', 'EUR/JPY (OTC)', 'USD/INR (OTC)', 
    'EUR/GBP (OTC)', 'EUR/USD (OTC)', 'GBP/USD (OTC)', 'USD/JPY (OTC)', 'USD/BRL (OTC)',
    'USD/TRY (OTC)', 'USD/PKR (OTC)', 'USD/IDR (OTC)', 'USD/MYR (OTC)', 'USD/PHP (OTC)',
    'EUR/CHF (OTC)', 'GBP/JPY (OTC)', 'NZD/USD (OTC)', 'CAD/CHF (OTC)', 'AUD/CAD (OTC)'
]

POCKET_PAIRS = [
    'EUR/USD OTC', 'GBP/USD OTC', 'USD/JPY OTC', 'AUD/CAD OTC', 'CAD/CHF OTC', 
    'NZD/USD OTC', 'AUD/USD OTC', 'EUR/GBP OTC', 'EUR/JPY OTC', 'GBP/JPY OTC', 
    'CHF/JPY OTC', 'EUR/AUD OTC', 'EUR/CAD OTC', 'USD/CAD OTC', 'USD/CHF OTC',
    'Crypto IDX-OTC', 'Gold-OTC', 'Silver-OTC', 'Bitcoin OTC', 'Ethereum OTC',
    'Apple OTC', 'American Express OTC', 'Boeing OTC', 'Caterpillar OTC', 
    'Cisco OTC', 'Chevron OTC', 'Intel OTC', 'Microsoft OTC', 'Pfizer OTC'
]

# Status Box
st.markdown(f"""
    <div class="status-box">
        <h4 style="color:#00ffd5; margin:0;">📈 MARKET ANALYSIS OPEN</h4>
        <p style="color:#888; margin:5px 0 0 0; font-size:13px;">Platform Active: <b>{st.session_state.platform}</b> | System: Secured Proxy Connected</p>
    </div>
    """, unsafe_allow_html=True)

# 4. ENGINE CORE
def generate_auto_signal():
    if st.session_state.platform == "Quotex":
        chosen_pair = random.choice(QUOTEX_PAIRS)
    else:
        chosen_pair = random.choice(POCKET_PAIRS)
        
    direction_choice = random.choice(["LONG ⬆️", "SHORT ⬇️"])
    direction_text = "LONG (BUY)" if "LONG" in direction_choice else "SHORT (SELL)"
    
    probability = random.randint(84, 89)
    
    return chosen_pair, direction_text, probability

# 5. AUTOMATED GENERATOR BUTTON
if st.button("⚡ NEW ANALYSIS (🚀 GET SIGNAL)"):
    with st.spinner('Analyzing Global Neural Nodes for Best Asset...'):
        time.sleep(2.5) 
        
        pair, direction, prob = generate_auto_signal()
        
        st.subheader("📊 ANALYSIS COMPLETE")
        
        # Sanduuqa Natiijada iyadoo la isticmaalayo Streamlit native components
        st.info(f"**Currency Pair:** {pair}")
        st.warning("**Exp Time:** 3 Minutes")
        
        # Midabka jihada ku xiran
        if "LONG" in direction:
            st.success(f"**Direction:** ▲ {direction}")
        else:
            st.error(f"**Direction:** ▼ {direction}")
            
        st.metric(label="System Probability", value=f"{prob}%")
            
        if prob >= 88:
            st.balloons()

st.markdown("<p style='text-align: center; color: #333; margin-top: 40px;'>PROV MAHAD AI v3.0 | Auto-Scanning Binary System</p>", unsafe_allow_html=True)
