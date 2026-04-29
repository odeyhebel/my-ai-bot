import streamlit as st
import pandas as pd
import numpy as np
import time
import json
import asyncio
import websockets

# 1. Configuration & Security
st.set_page_config(page_title="AI Auto-Trader Pro", layout="centered")

# Hubi in Secrets ay ku jiraan Streamlit
try:
    USER_EMAIL = st.secrets["PO_EMAIL"]
    USER_PASS = st.secrets["PO_PASSWORD"]
except:
    st.error("Secrets-ka laguma helin! Hubi 'App Settings -> Secrets' ee Streamlit.")

if 'consecutive_losses' not in st.session_state:
    st.session_state.consecutive_losses = 0

st.title("🤖 AI Auto-Trader (Live Connection)")

# 2. Risk Management (Sidebar)
with st.sidebar:
    st.header("Risk Management")
    max_losses = st.number_input("Xadka khasaaraha (Stop Loss)", min_value=1, value=2)
    trade_amount = st.number_input("Lacagta hal trade ($)", min_value=1.0, value=1.0)
    
    if st.session_state.consecutive_losses >= max_losses:
        st.error("🛑 BOT STOPPED: Xadkii khasaaraha waa la gaaray!")
        st.stop()

# 3. Pocket Option Connection Logic
async def connect_and_trade():
    # URL-kan waa kan saxda ah ee Websocket-ka
    uri = "wss://api-eu.pocketoption.com/socket.io/?EIO=4&transport=websocket"
    
    try:
        # Waxaan ku darnay 'ping_interval' si uusan xiriirku u 'Timeout' noqon
        async with websockets.connect(uri, ping_interval=5, ping_timeout=10) as websocket:
            st.toast("Isku xirka waa la bilaabay...")
            
            # Authentication Payload
            auth_payload = f'42["auth", {{"email": "{USER_EMAIL}", "password": "{USER_PASS}"}}]'
            await websocket.send(auth_payload)
            
            st.success(f"Lagu xiray: {USER_EMAIL}")
            
            while st.session_state.consecutive_losses < max_losses:
                response = await websocket.recv()
                
                # Muuji xogta live-ka ah ee soo dhacaysa
                with st.empty():
                    st.write(f"📡 Xog live ah: {response[:100]}...")
                
                await asyncio.sleep(0.5)
                
    except Exception as e:
        st.error(f"Cilad xiriir: {e}")

# 4. Interface Controls
if st.button("🚀 Start Live Auto-Trading"):
    with st.spinner("Raadinaya xiriirka broker-ka..."):
        asyncio.run(connect_and_trade())
