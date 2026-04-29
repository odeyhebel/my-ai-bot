import streamlit as st
import asyncio
import websockets
import json

# Configuration
st.set_page_config(page_title="AI Auto-Trader Pro", layout="centered")

try:
    USER_EMAIL = st.secrets["PO_EMAIL"]
    USER_PASS = st.secrets["PO_PASSWORD"]
except:
    st.error("Secrets-ka laguma helin! Hubi Streamlit Settings.")

async def connect_and_trade():
    # Waxaan u beddelnay URL-ka midka guud ee caalamiga ah
    uri = "wss://api-eu.pocketoption.com/socket.io/?EIO=4&transport=websocket"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    try:
        # Waxaan ku darnay 'extra_headers' si broker-ka uusan noo xannibin
        async with websockets.connect(uri, extra_headers=headers, ping_interval=5) as websocket:
            st.success("Xiriirka waa la helay! AI-du waxay bilaabaysaa login-ka...")
            
            # Authentication
            auth_payload = f'42["auth", {{"email": "{USER_EMAIL}", "password": "{USER_PASS}"}}]'
            await websocket.send(auth_payload)
            
            while True:
                response = await websocket.recv()
                with st.empty():
                    st.info(f"📡 Xog live ah: {response[:100]}")
                await asyncio.sleep(0.5)

    except Exception as e:
        st.error(f"Cilad xiriir: {str(e)}")

st.title("🤖 AI Auto-Trader (Live Connection)")

if st.button("🚀 Start Live Auto-Trading"):
    with st.spinner("Isku dayaya inuu la xirmo Pocket Option..."):
        asyncio.run(connect_and_trade())
