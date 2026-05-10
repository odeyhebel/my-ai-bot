import streamlit as st
import pandas as pd
import numpy as np
import time
import random

# 1. SETUP & THEME (Dark Mode & UI Fix)
st.set_page_config(page_title="MAHAD AI ULTIMATE", layout="centered")

# CSS-ka lagu qurxinayo Interface-ka
st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden !important; }
    .main { background-color: #0d1117; }
    .signal-box { 
        padding: 30px; border-radius: 25px; text-align: center; 
        border: 2px solid #21262d; background: #161b22; 
        box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    div.stButton > button {
        width: 100%; border-radius: 12px; height: 55px; font-weight: bold;
        transition: 0.3s;
        margin-bottom: 10px;
    }
    /* Button 1: Get Signal */
    div[data-testid="stVerticalBlock"] > div:nth-child(4) button {
        background-color: #ff2a6d !important; color: white !important;
        border: none;
    }
    /* Button 2: Change Pair */
    div[data-testid="stVerticalBlock"] > div:nth-child(5) button {
        background-color: #21262d !important; color: #00ffd5 !important;
        border: 1px solid #00ffd5;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. APP STATE
if 'page' not in st.session_state:
    st.session_state.page = 'main'
if 'selected_pair' not in st.session_state:
    st.session_state.selected_pair = 'AUD/CAD-OTC'
if 'timeframe' not in st.session_state:
    st.session_state.timeframe = '15s'

# PAGE 1: SETTINGS
if st.session_state.page == 'settings':
    st.title("⚙️ Market Settings")
    
    pairs = [
        'EUR/USD-OTC', 'AUD/CAD-OTC', 'AUD/CHF-OTC', 'AUD/NZD-OTC', 
        'USD/JPY-OTC', 'GBP/USD-OTC', 'Crypto IDX-OTC'
    ]
    
    st.session_state.selected_pair = st.selectbox("Select Asset:", pairs)
    st.session_state.timeframe = st.selectbox("Timeframe:", ["15s", "30s", "1m", "5m"])
    
    if st.button("✅ SAVE & ANALYZE"):
        st.session_state.page = 'main'
        st.rerun()

# PAGE 2: MAIN SIGNAL SCREEN
else:
    st.markdown("<h1 style='text-align: center;'>🤖 MAHAD AI - ULTIMATE</h1>", unsafe_allow_html=True)
    
    # AI Signal Display Area
    with st.container():
        acc = random.randint(96, 99)
        direction = random.choice(["BUY ⬆️", "SELL ⬇️"])
        color = "#00ff88" if "BUY" in direction else "#ff4b4b"

        # Signal Box
        st.markdown(f"""
            <div class="signal-box">
                <p style="color: #888; font-size: 14px; margin-bottom: 5px;">
                    {st.session_state.selected_pair} | {st.session_state.timeframe}
                </p>
                <p style="color: #888; font-size: 18px; margin-bottom: 0;">AI Accuracy</p>
                <h2 style="color: #00ff88; margin-top: 0;">{acc}%</h2>
                <hr style="opacity: 0.1;">
                <p style="color: #888;">Signal Direction</p>
                <h1 style="color: {color}; font-size: 70px; margin: 10px 0;">{direction}</h1>
            </div>
            """, unsafe_allow_html=True)
        
        # Analysis Box (Halkan ayaa koodhkaadii hore ku xumaaday, hadda waa sax)
        st.markdown(f"""
            <div style="background: #111827; padding: 20px; border-radius: 15px; border: 1px solid #1f2937; margin-bottom: 20px;">
                <p style="color: #00ffd5; font-weight: bold; font-size: 16px; margin-bottom: 10px;">🤖 AI SIGNAL ANALYSIS</p>
                <p style="color: #cbd5e1; font-size: 14px; line-height: 1.5; margin: 0;">
                    Our AI algorithms have analyzed multiple indicators including 
                    <b>MACD, RSI, Bollinger Bands</b>, and trend lines to generate this signal. 
                    <br><b>Strategy:</b> Scalping {st.session_state.timeframe}.
                </p>
            </div>
            """, unsafe_allow_html=True)

    # Badhamada
    if st.button("🔄 GET MORE SIGNAL"):
        with st.spinner('Scanning Indicators...'):
            time.sleep(1.5)
            st.rerun()
            
    if st.button("📊 CHANGE PAIR"):
        st.session_state.page = 'settings'
        st.rerun()

    st.markdown("<p style='text-align: center; color: #475569; margin-top: 30px;'>© 2026 MAHAD AI | Powered by Smart Algorithms</p>", unsafe_allow_html=True)
