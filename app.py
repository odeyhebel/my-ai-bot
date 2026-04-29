import streamlit as st
import asyncio
import websockets
import json

# 1. Setup iyo Amniga
st.set_page_config(page_title="AI Auto-Trader Pro", layout="centered")

# Hubinta in xogta login-ka ay ku jirto Secrets
if "PO_EMAIL" not in st.secrets or "PO_PASSWORD" not in st.secrets:
    st.error("Secrets-ka laguma helin! Hubi Settings -> Secrets.")
    st.stop()

USER_EMAIL = st.secrets["PO_EMAIL"]
USER_PASS = st.secrets["PO_PASSWORD"]

async def connect_and_trade():
    # Cinwaanka rasmiga ah ee caalamiga ah (Global Server)
    uri = "wss://api.pocketoption.com/socket.io/?EIO=4&transport=websocket"
    
    try:
        # Waxaan kordhinnay waqtiga isku xirka si uusan 'Timeout' u dhicin
        async with websockets.connect(uri, open_timeout=30) as websocket:
            st.success("✅ Isku xirka waa guulaystay! AI-du waxay bilaabaysaa login-ka...")
            
            # Fariinta Login-ka (Format-ka rasmiga ah)
            auth_payload = f'42["auth", {{"email": "{USER_EMAIL}", "password": "{USER_PASS}"}}]'
            await websocket.send(auth_payload)
            
            # Daawashada xogta live-ka ah
            while True:
                response = await websocket.recv()
                with st.empty():
                    st.info(f"📡 Xog live ah: {response[:100]}...")
                await asyncio.sleep(0.5)

    except Exception as e:
        st.error(f"❌ Cilad xiriir: {str(e)}")

# Interface-ka
st.title("🤖 AI Auto-Trader (Live Connection)")

if st.button("🚀 Start Live Auto-Trading"):
    with st.spinner("Isku dayaya inuu la xirmo Pocket Option..."):
        try:
            asyncio.run(connect_and_trade())
        except Exception as e:
            st.error(f"Cilad: {e}")
