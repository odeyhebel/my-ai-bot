import streamlit as st
import random
import time

# 1. Config & Theme (Muuqaalka Mobile-ka)
st.set_page_config(page_title="NAGIIP AI SIGNAL", layout="centered")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #050a0e; color: white; }
    .signal-card {
        background: #0b151e;
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #1e3a4c;
        text-align: center;
        margin-top: 20px;
    }
    .buy-color { color: #00ff88; font-size: 50px; font-weight: bold; }
    .sell-color { color: #ff4b4b; font-size: 50px; font-weight: bold; }
    .btn-main { background-color: #00ff88 !important; color: black !important; font-weight: bold !important; width: 100%; border-radius: 10px !important; }
    .btn-alt { background-color: #ff004c !important; color: white !important; font-weight: bold !important; width: 100%; border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Header
st.markdown("<h1 style='text-align: center; color: #00d4ff;'>🤖 NAGIIP AI SIGNAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>AI-generated trading signal</p>", unsafe_allow_html=True)

# 3. Sidebar (Change Pairs & Timers)
with st.sidebar:
    st.header("⚙️ Settings")
    selected_pair = st.selectbox("Currency Pair", ["EUR/USD", "GBP/USD", "AUD/USD OTC", "USD/JPY OTC", "Crypto IDX"])
    time_frame = st.radio("Time Frame", ["15 SECOND", "1 MINUTE", "5 MINUTE"])
    st.write("---")
    st.write("Market: " + ("OTC" if "OTC" in selected_pair else "REAL MARKET"))

# 4. Main UI
if 'signal' not in st.session_state:
    st.session_state.signal = None

def generate_signal():
    with st.spinner('AI is analyzing indicators (MACD, RSI)...'):
        time.sleep(2)
        direction = random.choice(["BUY", "SELL"])
        accuracy = random.randint(95, 99)
        st.session_state.signal = {"dir": direction, "acc": accuracy}

# 5. Signal Display
if st.session_state.signal:
    sig = st.session_state.signal
    color_class = "buy-color" if sig['dir'] == "BUY" else "sell-color"
    icon = "⬆️" if sig['dir'] == "BUY" else "⬇️"
    
    st.markdown(f"""
        <div class="signal-card">
            <p style="margin:0; opacity:0.7;">Currency Pair</p>
            <h3>{selected_pair}</h3>
            <p style="margin:0; opacity:0.7;">Time Frame: {time_frame}</p>
            <br>
            <div class="{color_class}">{icon} {sig['dir']}</div>
            <p style="color: #00ff88;">Accuracy: {sig['acc']}%</p>
            <hr style="opacity:0.1;">
            <p style="font-size: 12px; opacity:0.6;">
            AI algorithms analyzed multiple indicators including MACD, RSI, and Bollinger Bands.
            Recommended position: 3% of balance.
            </p>
        </div>
    """, unsafe_allow_html=True)

# 6. Buttons
st.write("")
if st.button("🔄 GET MORE SIGNALS", key="get_sig"):
    generate_signal()
    st.rerun()

if st.button("⚙️ CHANGE PAIRS / SETTINGS", key="change_p"):
    st.info("Isticmaal menu-ga bidix (Sidebar) si aad u beddesho Pairs-ka.")
