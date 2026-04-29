import streamlit as st
import asyncio
import websockets
import json

# 1. Setup
st.set_page_config(page_title="AI Auto-Trader Pro", layout="centered")

# Soo qaado xogta qarsoon
try:
    USER_EMAIL = st.secrets["PO_EMAIL"]
    USER_PASS = st.secrets["PO_PASSWORD"]
except Exception:
    st.error("Secrets-ka laguma helin! Hubi Streamlit Settings -> Secrets.")
    st.stop()

async def connect_and_trade():
    # Waxaan isku dayaynaa URL-ka rasmiga ah ee ugu deggan
    uri = "wss://api-eu.pocketoption.com/socket.io/?EIO=4&transport=websocket"
    
    try:
        # Waxaan kordhinnay waqtiga (timeout) si aanu dhaqso u go'in
        async with websockets.connect(uri, open_timeout=30, ping_interval=5) as websocket:
            st.success("Xiriirka waa la helay! AI-du waxay bilaabaysaa login-ka...")
            
            # Fariinta Login-ka
            auth_payload = f'42["auth", {{"email": "{USER_EMAIL}", "password": "{USER_PASS}"}}]'
            await websocket.send(auth_payload)
            
            # Loop-ka akhrinta xogta
            while True:
                response = await websocket.recv()
                # Muuji xogta live-ka ah ee suuqa
                with st.empty():
                    st.info(f"📡 Xog live ah: {response[:100]}")
                await asyncio.sleep(0.5)

    except Exception as e:
        # Tani waxay soo bandhigaysaa cilad kasta oo dhacda
        st.error(f"Cilad xiriir: {str(e)}")

# Interface-ka
st.title("🤖 AI Auto-Trader (Live Connection)")

if st.button("🚀 Start Live Auto-Trading"):
    with st.spinner("Isku dayaya inuu la xirmo Pocket Option..."):
        try:
            asyncio.run(connect_and_trade())
        except Exception as e:
            st.error(f"Cilad aan la filayn: {e}")
