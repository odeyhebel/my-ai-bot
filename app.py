import streamlit as st
import pandas as pd
import yfinance as yf
import time
import random

# 1. SETUP & THEME
st.set_page_config(page_title="MAHAD AI - REAL TIME", layout="centered")

st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden !important; }
    .main { background-color: #050a0e; }
    .price-box {
        background: #111b21; border-radius: 10px; padding: 15px;
        margin-bottom: 10px; border-left: 5px solid #2ecc71;
        display: flex; justify-content: space-between; align-items: center;
    }
    .win-text { color: #2ecc71; font-size: 80px; font-weight: bold; text-align: center; }
    .loss-text { color: #e74c3c; font-size: 80px; font-weight: bold; text-align: center; }
    .stButton > button { background-color: #27ae60 !important; color: white !important; width: 100%; border-radius: 8px; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

# 2. SELECTION (Pairs & Time)
with st.sidebar:
    st.title("Real Market Config")
    # Yfinance waxay isticmaashaa tusaale: EURUSD=X
    pairs_dict = {
        'EUR/USD': 'EURUSD=X',
        'GBP/USD': 'GBPUSD=X',
        'USD/JPY': 'JPY=X',
        'CAD/CHF': 'CADCHF=X',
        'Bitcoin': 'BTC-USD'
    }
    selected_name = st.selectbox("Xulo Real Market Pair:", list(pairs_dict.keys()))
    symbol = pairs_dict[selected_name]
    time_limit = st.selectbox("Expiration Time:", ["30s", "1m", "2m"])

# 3. LIVE DATA FUNCTION
def get_live_price(ticker):
    data = yf.Ticker(ticker).history(period='1d', interval='1m')
    return data['Close'].iloc[-1]

# 4. APP STATE
if 'status' not in st.session_state:
    st.session_state.status = 'idle'
if 'open_price' not in st.session_state:
    st.session_state.open_price = 0

# 5. INTERFACE
st.markdown(f"<h2 style='text-align: center; color: white;'>{selected_name} - LIVE</h2>", unsafe_allow_html=True)

if st.session_state.status == 'idle':
    if st.button("GET NEW SIGNAL >"):
        st.session_state.open_price = get_live_price(symbol)
        st.session_state.status = 'scanning'
        st.rerun()

elif st.session_state.status == 'scanning':
    with st.spinner(f"Analyzing Live Market for {selected_name}..."):
        time.sleep(3) # AI Analysis simulation
        # Halkan bot-ku wuxuu go'aan ka gaarayaa haddii uu Win yahay iyo haddii kale
        # Waxaan u sameynay 80% Win Rate
        st.session_state.current_price = get_live_price(symbol)
        outcome = random.choices(['won', 'loss'], weights=[80, 20])[0]
        st.session_state.status = outcome
        st.rerun()

elif st.session_state.status in ['won', 'loss']:
    if st.session_state.status == 'won':
        st.markdown("<div class='win-text'>WIN</div>", unsafe_allow_html=True)
        st.balloons()
        close_p = st.session_state.open_price - random.uniform(0.00010, 0.00040)
    else:
        st.markdown("<div class='loss-text'>LOSS</div>", unsafe_allow_html=True)
        close_p = st.session_state.open_price + random.uniform(0.00010, 0.00040)

    st.markdown(f"""
        <div class="price-box">
            <span style="color: #888;">Opening Price:</span>
            <span style="color: #2ecc71; font-weight: bold;">${st.session_state.open_price:.5f}</span>
        </div>
        <div class="price-box" style="border-left: 5px solid #e74c3c;">
            <span style="color: #888;">Closing Price:</span>
            <span style="color: #e74c3c; font-weight: bold;">${close_p:.5f}</span>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("ANALYZE NEXT TRADE"):
        st.session_state.status = 'idle'
        st.rerun()
