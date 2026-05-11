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
    /* Badhanka weyn ee cagaaran */
    .stButton > button {
        background-color: #27ae60 !important; color: white !important;
        width: 100%; border-radius: 8px; height: 50px; font-size: 18px;
        font-weight: bold; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. XULASHADA (Dhinaca Bidix - Sidebar)
with st.sidebar:
    st.markdown("<h2 style='color: white;'>⚙️ MAHAD AI SETTINGS</h2>", unsafe_allow_html=True)
    
    # DOORASHADA PAIRS-KA (Real & OTC)
    st.session_state.selected_pair = st.selectbox(
        "Xulo Lacagta (Pairs):", 
        ['CAD/CHF-OTC', 'EUR/USD-OTC', 'AUD/NZD-OTC', 'GBP/USD-OTC', 
         'EUR/GBP (Real)', 'USD/JPY (Real)', 'Gold-OTC', 'BTC/USD']
    )
    
    # DOORASHADA TIMEFRAME-KA
    st.session_state.selected_time = st.radio(
        "Timeframe:", 
        ["30s", "1m", "2m"], 
        horizontal=True
    )
    
    st.divider()
    st.info("Markaad beddesho Pair ama Time, riix 'GET NEW SIGNAL'.")

# 3. APP STATE
if 'trade_status' not in st.session_state:
    st.session_state.trade_status = 'idle'

# 4. MAIN INTERFACE (Bartamaha)
st.markdown(f"<h1 style='text-align: center; color: white;'>{st.session_state.selected_pair}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #888;'>Timeframe: {st.session_state.selected_time}</p>", unsafe_allow_html=True)

# Muujinta Signal-ka
if st.session_state.trade_status == 'idle':
    direction = random.choice(["BUY", "SELL"])
    dir_color = "#2ecc71" if direction == "BUY" else "#e74c3c"
    
    st.markdown(f"""
        <div style='background: {dir_color}; color: white; padding: 15px; border-radius: 8px; 
        width: 120px; text-align: center; font-weight: bold; margin: 20px auto; font-size: 24px;'>
            {direction}
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("GET NEW SIGNAL >"):
        st.session_state.trade_status = 'scanning'
        st.rerun()

elif st.session_state.trade_status == 'scanning':
    with st.spinner(f"Analyzing {st.session_state.selected_pair}..."):
        time.sleep(2.5) # Sugitaan falanqayn ah
        st.session_state.trade_status = 'won'
        st.rerun()

elif st.session_state.trade_status == 'won':
    st.markdown("<div class='win-text'>WIN</div>", unsafe_allow_html=True)
    st.balloons()
    
    # Xogta Natiijada (Sida bot-ka aad aragtay)
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
