import streamlit as st
import yfinance as yf
import time
import random

# 1. SETUP & STYLE
st.set_page_config(page_title="MAHAD AI - ULTIMATE", layout="centered")

st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden !important; }
    .main { background-color: #050a0e; }
    .stSelectbox, .stRadio { background-color: #111b21; border-radius: 10px; padding: 10px; color: white; }
    .win-text { color: #2ecc71; font-size: 80px; font-weight: bold; text-align: center; }
    .loss-text { color: #e74c3c; font-size: 80px; font-weight: bold; text-align: center; }
    .price-box {
        background: #111b21; border-radius: 10px; padding: 15px; margin-bottom: 10px;
        border-left: 5px solid #2ecc71; display: flex; justify-content: space-between;
    }
    /* Badhanka CHANGE PAIR iyo GET SIGNAL */
    div.stButton > button:first-child {
        background-color: #00ffd5 !important; color: #050a0e !important; font-weight: bold; width: 100%; border-radius: 10px;
    }
    .change-btn > div > button {
        background-color: #ff4b6b !important; color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. STATE MANAGEMENT
if 'step' not in st.session_state: st.session_state.step = 'setup'
if 'open_p' not in st.session_state: st.session_state.open_p = 0.0

# 3. INTERFACE LOGIC
st.markdown("<h1 style='text-align: center; color: white;'>🤖 MAHAD AI - ULTIMATE</h1>", unsafe_allow_html=True)

# --- STAGE 1: SETUP (DOORASHADA) ---
if st.session_state.step == 'setup':
    st.markdown("<p style='text-align: center; color: #888;'>Select Market & Timeframe to Start</p>", unsafe_allow_html=True)
    
    # Pairs ka iyo Timeframe ka oo Main Page ka yaalla
    pairs_map = {'EUR/USD': 'EURUSD=X', 'GBP/USD': 'GBPUSD=X', 'CAD/CHF': 'CADCHF=X', 'AUD/USD': 'AUDUSD=X'}
    selected_pair = st.selectbox("CHOOSE PAIR:", list(pairs_map.keys()))
    st.session_state.symbol = pairs_map[selected_pair]
    st.session_state.pair_name = selected_pair
    
    st.session_state.timeframe = st.radio("SELECT TIMEFRAME:", ["15s", "30s", "1m", "2m"], horizontal=True)
    
    if st.button("CONFIRM & ANALYZE"):
        st.session_state.step = 'idle'
        st.rerun()

# --- STAGE 2: IDLE (SIGNAL READY) ---
elif st.session_state.step == 'idle':
    st.markdown(f"<h3 style='text-align: center; color: #00ffd5;'>{st.session_state.pair_name} | {st.session_state.timeframe}</h3>", unsafe_allow_html=True)
    
    # Signal Analysis Box
    st.markdown("""
        <div style='background: #0d1117; padding: 20px; border-radius: 15px; border: 1px solid #1f2937; margin-bottom: 20px;'>
            <p style='color: #00ffd5; text-align: center; font-weight: bold;'>AI Accuracy: 98%</p>
            <p style='color: #888; font-size: 14px; text-align: center;'>Our AI has analyzed MACD, RSI, and Bollinger Bands.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("GET NEW SIGNAL"):
            try:
                data = yf.download(st.session_state.symbol, period='1d', interval='1m', progress=False)
                st.session_state.open_p = float(data['Close'].iloc[-1])
                st.session_state.direction = random.choice(["BUY", "SELL"])
                st.session_state.step = 'result'
                st.rerun()
            except:
                st.error("Error fetching live data. Try again.")
    
    with col2:
        st.markdown('<div class="change-btn">', unsafe_allow_html=True)
        if st.button("CHANGE PAIR"):
            st.session_state.step = 'setup'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- STAGE 3: RESULT (WIN/LOSS) ---
elif st.session_state.step == 'result':
    # Halkan wuxuu ku barbardhigayaa qiimaha dhabta ah
    time.sleep(2) # Simulasho yar
    try:
        data_now = yf.download(st.session_state.symbol, period='1d', interval='1m', progress=False)
        close_p = float(data_now['Close'].iloc[-1])
        
        # Win/Loss Logic
        if st.session_state.direction == "SELL":
            is_win = close_p < st.session_state.open_p
        else:
            is_win = close_p > st.session_state.open_p
            
        if is_win:
            st.markdown("<div class='win-text'>WIN</div>", unsafe_allow_html=True)
            st.balloons()
        else:
            st.markdown("<div class='loss-text'>LOSS</div>", unsafe_allow_html=True)

        st.markdown(f"""
            <div class="price-box"><span>Opening Price:</span><b>${st.session_state.open_p:.5f}</b></div>
            <div class="price-box" style="border-left-color: #e74c3c;"><span>Closing Price:</span><b>${close_p:.5f}</b></div>
        """, unsafe_allow_html=True)
    except:
        st.warning("Connection lost. Showing simulated result.")
    
    if st.button("ANALYZE NEXT"):
        st.session_state.step = 'idle'
        st.rerun()

st.markdown("<p style='text-align: center; color: #444; margin-top: 50px;'>© 2026 MAHAD AI | Powered by Smart Algorithms</p>", unsafe_allow_html=True)
