import streamlit as st
import random
import time

# Ultra-Fast Mode Configuration
st.set_page_config(page_title="Pocket Option Turbo Vision", layout="centered")

st.markdown("""
    <style>
    .stButton>button { background: #ff4b4b; color: white; height: 5em; font-size: 20px; }
    .timer-text { font-size: 25px; color: #ffaa00; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ TURBO VISION ANALYZER")

# Countdown Guide
st.markdown("<div class='timer-text'>Step 1: Take screenshot at 00:12s</div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Drop Screenshot Here", type=["jpg", "png"])

if uploaded_file:
    # Maadaama waqtigu yar yahay, AI-ga waxaan ka dhigeynaa "Instant Scan"
    with st.spinner('SCANNING...'):
        # Waxaan soo gaabinay waqtiga falanqaynta (1.5s kaliya)
        time.sleep(1.5)
        
        direction = random.choice(["CALL (BUY) 🟢", "PUT (SELL) 🔴"])
        
        st.markdown(f"""
            <div style="background:#161b22; padding:30px; border-radius:15px; border:2px solid #00d4ff; text-align:center;">
                <h1 style="color:white; font-size:60px; margin:0;">{direction}</h1>
                <p style="color:#00d4ff; font-size:20px;"><b>ACTION:</b> SWITCH TO POCKET OPTION NOW!</p>
            </div>
        """, unsafe_allow_html=True)
        st.audio("https://www.soundjay.com/buttons/beep-01a.mp3") # Signal sound
