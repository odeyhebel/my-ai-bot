import streamlit as st
import asyncio
import websockets
import json

# 1. Setup iyo Amniga
st.set_page_config(page_title="AI Auto-Trader Pro", layout="centered")

try:
    USER_EMAIL = st.secrets["PO_EMAIL"]
    USER_PASS = st.secrets["PO_PASSWORD"]
except:
    st.error("Secrets-ka laguma helin! Fadlan ku dar PO_EMAIL iyo PO_PASSWORD gudaha Streamlit Secrets.")

async def connect_and_trade():
    # Waxaan u beddelnay URL-ka midka tooska ah ee broker-ka
    uri = "wss://api.pocketoption.com/socket.io/?EIO=4&transport=websocket"
    
    # Waxaan ka saarnay 'extra_headers' si aan looga helin ciladda 'unexpected keyword'
    try:
        async with websockets.connect(uri, ping_interval=5) as websocket:
            st.success("Xiriirka waa la helay! AI-du waxay bilaabaysaa login-ka...")
            
            # Authentication (Format-ka 42 waa ka rasmiga ah)
            auth_payload = f'42["auth", {{"email": "{USER_EMAIL}", "password": "{USER_PASS}"}}]'
            await websocket.send(auth_payload)
            
            # Loop-ka akhrinta xogta
            while True:
                response = await websocket.recv()
                # Muuji xogta live-ka ah
                with st.empty():
                    st.info(f"📡 Xog live ah: {response[:100]}")
                await asyncio.sleep(0.5)

    except Exception as e:
        # Tani waxay soo qabataa haddii uu jiro Error kale
        st.error(f"Cilad xiriir: {str(e)}")

st.title("🤖 AI Auto-Trader (Live Connection)")

# Interface-ka
if st.button("🚀 Start Live Auto-Trading"):
    if not USER_EMAIL or not USER_PASS:
        st.warning("Fadlan marka hore geli Email-ka iyo Password-ka Secrets-ka.")
    else:
        with st.spinner("Isku dayaya inuu la xirmo Pocket Option..."):
            asyncio.run(connect_and_trade())
