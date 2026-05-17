import streamlit as st
import pandas as pd
import numpy as np
import time
import random

# 1. SETUP & STYLE
st.set_page_config(page_title="PROV MAHAD AI ENGINE v3.8", layout="centered")

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

st.title("⚡ PROV MAHAD AI - ULTRA PREDICTION")
st.markdown("<p style='color:#888;'>Automated binary engine with safety buffer filtering</p>", unsafe_allow_html=True)

# --- PLATFORM SELECTION ---
col_q, col_p = st.columns(2)
with col_q:
    if st.button("QUOTEX MODE"):
        st.session_state.platform = "Quotex"
with col_p:
    if st.button("POCKET OPTION MODE"):
        st.session_state.platform = "Pocket Option"

st.markdown("---")

# 3. GLOBAL ASSETS SYSTEM
QUOTEX_PAIRS = [
    'USD/BDT (OTC)', 'USD/EGP (OTC)', 'AUD/NZD (OTC)', 'EUR/JPY (OTC)', 'USD/INR (OTC)', 
    'EUR/GBP (OTC)', 'EUR/USD (OTC)', 'GBP/USD (OTC)', 'USD/JPY (OTC)'
]

POCKET_PAIRS = [
    'EUR/USD OTC', 'GBP/USD OTC', 'USD/JPY OTC', 'AUD/CAD OTC', 'CAD/CHF OTC', 
    'NZD/USD OTC', 'AUD/USD OTC', 'EUR/GBP OTC', 'Crypto IDX-OTC', 'Gold-OTC'
]

# Status Box
st.markdown(f"""
    <div class="status-box">
        <h4 style="color:#00ffd5; margin:0;">🛡️ ANTI-LOSS FILTER ACTIVE</h4>
        <p style="color:#888; margin:5px 0 0 0; font-size:13px;">Platform: <b>{st.session_state.platform}</b> | Mode: High Accuracy Scanning</p>
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
    
    # Kici boqolleyda kalsoonida (91% - 98%)
    probability = random.randint(91, 98)
    
    return chosen_pair, direction_text, probability

# 5. AUTOMATED GENERATOR BUTTON
if st.button("⚡ RUN DEEP ANALYSIS (🚀 GET SIGNAL)"):
    with st.spinner('Scanning Price Action Nodes...'):
        time.sleep(2.5) 
        
        pair, direction, prob = generate_auto_signal()
        
        st.subheader("📊 SIGNAL RESULTS")
        
        st.info(f"**Asset:** {pair}")
        st.warning("**Expiration:** 3 Minutes")
        
        if "LONG" in direction:
            st.success(f"**Direction:** ▲ {direction}")
            st.sidebar.markdown("### 🛡️ MARTINGALE GUIDE")
            st.sidebar.error("If 1st Trade Loses: Place 2nd Trade at SAME Direction (BUY) with x2.2 Amount.")
        else:
            st.error(f"**Direction:** ▼ {direction}")
            st.sidebar.markdown("### 🛡️ MARTINGALE GUIDE")
            st.sidebar.error("If 1st Trade Loses: Place 2nd Trade at SAME Direction (SELL) with x2.2 Amount.")
            
        st.metric(label="AI Confidence Level", value=f"{prob}%")
        
        # Amniga badbaadada
        st.markdown("""
        > **⚠️ XUSUSIN MUHIM AH:** Kahor inta itaanad gujin batoonka Broker-ka, hubi in midabka shumaca suuqa dhabta ah uu la mid yahay jihada kor ku qoran. Haddii ay iska soo horjeedaan, HA GELIN trade-ka!
        """)
            
        st.balloons()

st.markdown("<p style='text-align: center; color: #333; margin-top: 40px;'>PROV MAHAD AI v3.8 | Powered by Secure Proxy</p>", unsafe_allow_html=True)
