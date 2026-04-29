import streamlit as st
import pandas as pd
import numpy as np
import time
import json

# 1. Configuration & Security
st.set_page_config(page_title="AI Auto-Trader Safe Mode", layout="centered")

try:
    USER_EMAIL = st.secrets["PO_EMAIL"]
    USER_PASS = st.secrets["PO_PASSWORD"]
except:
    st.warning("Fadlan ku dar Secrets-ka Streamlit Dashboard-ka.")

if 'consecutive_losses' not in st.session_state:
    st.session_state.consecutive_losses = 0

st.title("🤖 AI Auto-Trader (Safety Enabled)")

# 2. Risk Management (Sidebar)
with st.sidebar:
    st.header("Risk Management")
    max_losses = st.number_input("Xadka khasaaraha (Stop Loss)", min_value=1, value=2)
    trade_amount = st.number_input("Lacagta hal trade ($)", min_value=1.0, value=1.0)
    
    if st.session_state.consecutive_losses >= max_losses:
        st.error("🛑 BOT STOPPED: Xadkii khasaaraha waa la gaaray!")
        st.stop()

# 3. Trading Logic (RSI & MA)
def analyze_data():
    # Tusaale xogta live-ka ah (Halkan Websocket ayaa geli lahaa)
    prices = np.random.randn(100).cumsum() + 100
    df = pd.DataFrame(prices, columns=['close'])
    
    # Simple Moving Average
    df['ma_7'] = df['close'].rolling(window=7).mean()
    df['ma_25'] = df['close'].rolling(window=25).mean()
    
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Shuruudda Signal-ka
    if last['ma_7'] > last['ma_25'] and prev['ma_7'] <= prev['ma_25']:
        return "CALL"  # BUY
    elif last['ma_7'] < last['ma_25'] and prev['ma_7'] >= prev['ma_25']:
        return "PUT"   # SELL
    return "WAIT"

# 4. Execution
status = st.empty()
if st.button("Start Auto-Trading"):
    st.success(f"Lagu xiray: {USER_EMAIL}")
    
    while st.session_state.consecutive_losses < max_losses:
        decision = analyze_data()
        
        if decision != "WAIT":
            status.warning(f"🎯 AI Signal: {decision}! Trade-ka waa la riday...")
            # Halkan trade-ka dhabta ah ayaa ka dhacaya
            time.sleep(60) # Sug natiijada
            
            # Tusaale: Haddii trade-ku khasaaro
            # st.session_state.consecutive_losses += 1
        else:
            status.info("⏳ Suuqay ayaa la baarayaa... fursad ammaan ah ayaa la sugayaa.")
        
        time.sleep(2)
