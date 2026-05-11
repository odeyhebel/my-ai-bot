import streamlit as st
import time
import random

# 1. SETUP & UI DESIGN
st.set_page_config(page_title="MAHAD AI - V2 PRO", layout="centered")

st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden !important; }
    .main { background-color: #050a0e; }
    .price-box {
        background: #111b21; border-radius: 10px; padding: 15px;
        margin-bottom: 10px; border-left: 5px solid #2ecc71;
        display: flex; justify-content: space-between; align-items: center;
    }
    .win-text {
        color: #2ecc71; font-size: 80px; font-weight: bold;
        text-align: center; text-shadow: 0px 0px 20px rgba(46, 204, 113, 0.5);
    }
    .stButton > button {
        background-color: #27ae60 !important; color: white !important;
        width: 100%; border-radius: 8px; height: 50px; font-size: 18px;
        font-weight: bold;
    }
    .settings-label { color: #888; font-size: 14px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. APP STATE
if 'trade_status' not in st.session_state:
    st.session_state.trade_status = 'idle'
if 'selected_pair' not in st.session_state:
    st.session_state.selected_pair = 'CAD/CHF-OTC'
if 'selected_time' not in st.session_state:
    st.session_state.selected_time = '2m'

# 3. SIDEBAR / SETTINGS
with st.sidebar:
    st.title("⚙️ Bot Settings")
    
    # Isku darka Real iyo OTC Pairs
    all_pairs = [
        'CAD/CHF-OTC', 'EUR/USD-OTC', 'AUD/NZD-OTC', 'GBP/USD-OTC',
        'EUR/GBP (Real)', 'USD/JPY (Real)', 'BTC/USD', 'Gold-OTC'
    ]
    st.session_state.selected_pair = st.selectbox("Xulo Lacagta (Asset):", all_pairs)
    
    # Waqtiyada kala duwan
    st.session_state.selected_time = st.selectbox("Trade Time:", ["30s", "1m", "2m"])
    
    st.info("Fariin: Markaad lacagta beddesho, riix 'Get New Signal'.")

# 4. MAIN INTERFACE
st.markdown(f"<h2 style='text-align: center; color: white;'>{st.session_state.selected_pair}</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #888;'>Timeframe: {st.session_state.selected_time}</p>", unsafe_allow_html=True)

# Muujinta Signal-ka
if st.session_state.trade_status == 'idle':
    direction = random.choice(["BUY", "SELL"])
    dir_color = "#2ecc71" if direction == "BUY" else "#e74c3c"
    
    st.markdown(f"""
        <div style='background: {dir_color}; color: white; padding: 10px; border-radius: 5px; 
        width: 100px; text-align: center; font-weight: bold; margin: 0 auto 20px auto;'>{direction}</div>
    """, unsafe_allow_html=True)
    
    if st.button("GET NEW SIGNAL >"):
        st.session_state.trade_status = 'scanning'
        st.rerun()

elif st.session_state.trade_status == 'scanning':
    with st.spinner(f"Analyzing {st.session_state.selected_pair} for {st.session_state.selected_time}..."):
        time.sleep(2.5) # Simulasho falanqayn ah
        st.session_state.trade_status = 'won'
        st.rerun()

elif st.session_state.trade_status == 'won':
    # Dabaaldegga (WIN) - Sida sawirkaaga
    st.markdown("<div class='win-text'>WIN</div>", unsafe_allow_html=True)
    st.balloons()
    
    # Opening & Closing Prices - Sida bot-ka aad aragtay
    # Waxaan u sameeyay nambarro isbeddelaya si ay run ugu dhowaadaan
    base_price = random.uniform(0.50000, 1.20000)
    st.markdown(f"""
        <div class="price-box">
            <span style="color: #888;">Opening Price:</span>
            <span style="color: #2ecc71; font-weight: bold;">${base_price:.5f}</span>
        </div>
        <div class="price-box" style="border-left: 5px solid #e74c3c;">
            <span style="color: #888;">Closing Price:</span>
            <span style="color: #e74c3c; font-weight: bold;">${(base_price - 0.00014):.5f}</span>
        </div>
        <div style="background: #111b21; padding: 15px; border-radius: 10px; text-align: center; margin-top: 10px;">
             <span style="color: #2ecc71; font-size: 20px; font-weight: bold;">Profit: +$130.00</span>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("ANALYZE NEXT TRADE"):
        st.session_state.trade_status = 'idle'
        st.rerun()

st.markdown("<p style='text-align: center; color: #444; margin-top: 50px;'>© 2026 MAHAD AI - V2 PRO | Based on Smart Price Action</p>", unsafe_allow_html=True)
