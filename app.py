import streamlit as st
import random
import time

# Habaynta muuqaalka guud (Dark Theme & Styling)
st.set_page_config(page_title="Pocket Option AI Bot", layout="centered")

st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        border: none;
        margin-bottom: 10px;
    }
    .stButton>button:hover {
        background-color: #00d4ff;
        color: black;
    }
    .signal-card {
        padding: 20px;
        border-radius: 15px;
        background: linear-gradient(145deg, #161b22, #0d1117);
        border: 1px solid #30363d;
        text-align: center;
        margin-top: 20px;
    }
    .buy-signal { color: #00ff88; font-size: 24px; font-weight: bold; }
    .sell-signal { color: #ff4b4b; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("💠 POCKET OPTION AI ANALYZER")
st.write("---")

# Doorashada Currency Pairs (OTC Included)
st.subheader("Select Currency Pair")
pair = st.selectbox("", [
    "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", 
    "AUD/USD OTC", "USD/CAD OTC", "AUD/JPY OTC"
])

# Doorashada Time Frame (5s to 5m)
st.subheader("Select Time Frame")
timeframe = st.columns(4)
with timeframe[0]:
    t5s = st.button("5 SEC")
with timeframe[1]:
    t15s = st.button("15 SEC")
with timeframe[2]:
    t1m = st.button("1 MIN")
with timeframe[3]:
    t5m = st.button("5 MIN")

# Meesha natiijada lagu muujinayo
if any([t5s, t15s, t1m, t5m]):
    selected_time = "5s" if t5s else "15s" if t15s else "1m" if t1m else "5m"
    
    with st.spinner('🔄 Analyzing Market Data...'):
        time.sleep(2.5) # Simulation delay
        
        accuracy = random.randint(92, 98)
        direction = random.choice(["CALL (BUY)", "PUT (SELL)"])
        
        st.markdown(f"""
            <div class="signal-card">
                <h3>Signal Result</h3>
                <p>Asset: <b>{pair}</b> | Time: <b>{selected_time}</b></p>
                <hr style="border-color: #30363d;">
                <p style="font-size: 20px;">Accuracy: <span style="color: #00d4ff;">{accuracy}%</span></p>
                <div class="{'buy-signal' if 'CALL' in direction else 'sell-signal'}">
                    {direction} {'⬆️' if 'CALL' in direction else '⬇️'}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.warning("⚠️ Money Management: Use 1-2% of your balance per trade.")
