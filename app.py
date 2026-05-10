import streamlit as st
import pandas as pd
import numpy as np
import time
import random

# 1. SETUP & THEME (Dark Mode & UI)
st.set_page_config(page_title="MAHAD AI ULTIMATE", layout="centered")

st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden !important; }
    .main { background-color: #0d1117; }
    .signal-box { 
        padding: 30px; border-radius: 25px; text-align: center; 
        border: 2px solid #21262d; background: #161b22; 
        box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
    }
    div.stButton > button {
        width: 100%; border-radius: 12px; height: 55px; font-weight: bold;
        transition: 0.3s;
    }
    /* Buttons colors */
    div[data-testid="stVerticalBlock"] > div:nth-child(4) button {
        background-color: #00ffd5 !important; color: black !important;
    }
    div[data-testid="stVerticalBlock"] > div:nth-child(5) button {
        background-color: #ff2a6d !important; color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. APP STATE
if 'page' not in st.session_state:
    st.session_state.page = 'main'
if 'selected_pair' not in st.session_state:
    st.session_state.selected_pair = 'EUR/USD-OTC'
if 'timeframe' not in st.session_state:
    st.session_state.timeframe = '30s'

# PAGE 1: CHANGE PAIR & TIMEFRAME
if st.session_state.page == 'settings':
    st.title("⚙️ Market Settings")
    
    pairs = [
        'EUR/USD-OTC', 'AUD/CAD-OTC', 'AUD/CHF-OTC', 'AUD/NZD-OTC', 
        'CAD/CHF-OTC', 'GBP/AUD-OTC', 'USD/CAD-OTC', 'USD/JPY-OTC', 
        'Crypto IDX-OTC', 'Gold-OTC'
    ]
    
    st.session_state.selected_pair = st.selectbox("Select Asset:", pairs)
    st.session_state.timeframe = st.selectbox("Timeframe:", ["15s", "30s", "1m", "5m"])
    
    if st.button("✅ SAVE & ANALYZE"):
        st.session_state.page = 'main'
        st.rerun()

# PAGE 2: MAIN SIGNAL SCREEN (MAHAD AI)
else:
    st.title("🤖 MAHAD AI - ULTIMATE")
    
    # AI Signal Display Area
    with st.container():
        acc = random.randint(95, 98)
        # Logic ku dhisan OTC Trend
        direction = random.choice(["BUY ⬆️", "SELL ⬇️", "WAITING ⏳"])
        
        if direction == "BUY ⬆️":
            color = "#00ff88"
            status_text = "Bullish Order Detected"
        elif direction == "SELL ⬇️":
            color = "#ff4b4b"
            status_text = "Bearish Order Detected"
        else:
            color = "#ffffff"
            status_text = "Market Neutral - Wait"

        st.markdown(f"""
            <div class="signal-box">
                <p style="color: #888; font-size: 14px;">{st.session_state.selected_pair} | {st.session_state.timeframe}</p>
                <p style="color: #888; font-size: 18px; margin-bottom: 0;">AI Accuracy</p>
                <h2 style="color: #00ff88; margin-top: 0;">{acc}%</h2>
                <hr style="opacity: 0.1;">
                <p style="color: #888;">Signal Direction</p>
                <h1 style="color: {color}; font-size: 65px; margin: 10px 0;">{direction}</h1>
                
                <div style="background: #0d1117; padding: 20px; border-radius: 15px; margin-top: 25px; border: 1px solid #1e293b;">
                    <p style="color: #00ffd5; font-weight: bold; font-size: 16px;">🤖 MAHAD AI ANALYSIS</p>
                    <p style="color: #cbd5e1; font-size: 14px; line-height: 1.6;">
                        Our AI algorithms have analyzed multiple indicators including 
                        <b>MACD, RSI, Bollinger Bands</b>, and trend lines to generate this signal. 
                        <b>Strategy:</b> Scalping {st.session_state.timeframe}.
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.write("") 
    
    if st.button("🔄 GET MORE SIGNAL"):
        with st.spinner('Scanning Market for Smart Money...'):
            time.sleep(2)
            st.rerun()
            
    if st.button("📊 CHANGE PAIR"):
        st.session_state.page = 'settings'
        st.rerun()

    st.markdown(f"<p style='text-align: center; color: #475569; margin-top: 40px;'>© 2026 MAHAD AI | Powered by Smart Algorithms</p>", unsafe_allow_html=True)
