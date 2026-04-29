import streamlit as st
import asyncio
import websockets
import json

# 1. Setup
st.set_page_config(page_title="AI Auto-Trader Pro", layout="centered")

try:
    USER_EMAIL = st.secrets["PO_EMAIL"]
    USER_PASS = st.secrets["PO_PASSWORD"]
except:
    st.error("Secrets-ka laguma helin! Hubi Streamlit Secrets.")
    st.stop()

async def connect_and_trade():
    # URL-ka rasmiga ah (EU Server)
    uri = "wss://api-eu.pocketoption.com/socket.io/?EIO=4&transport=websocket"
    
    # Kani wuxuu bot-ka ka dhigayaa qof caadi ah oo browser ka soo galaya
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    try:
        # Waxaan kordhinay 'open_timeout' si uusan dhaqso u go'in
        async with websockets.connect(uri, extra_headers=headers, open_timeout=20, ping_interval=5) as websocket:
            st.success("Xiriirka waa la helay! AI-du waxay bilaabaysaa login-ka...")
            
            # Authentication
            auth_payload = f'42["auth", {{"email": "{USER_EMAIL}", "password": "{USER_PASS}"}}]'
            await websocket.send(auth_payload)
            
            while True:
                response = await websocket.recv()
                # Nadiifi qoraalka (Tirtir 42-ka hore haddii loo baahdo)
                clean_data = response.replace('42', '', 1) if response.startswith('42') else response
                
                with st.empty():
                    st.info(f"📡 Xog live ah: {clean_data[:100]}")
                await asyncio.sleep(0.5)

    except Exception as e:
        st.error(f"Cilad xiriir: {str(e)}")

st.title("🤖 AI Auto-Trader (Live Connection)")

if st.button("🚀 Start Live Auto-Trading"):
    with st.spinner("Isku dayaya inuu la xirmo Pocket Option (Bypass Mode)..."):
        asyncio.run(connect_and_trade())
