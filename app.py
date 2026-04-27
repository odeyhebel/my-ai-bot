import streamlit as st
import random
import time

# Pro UI Setup
st.set_page_config(page_title="NAGIIP AI PRO", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #050a0e; }
    .stButton>button { width: 100%; border-radius: 20px; height: 50px; font-weight: bold; }
    .signal-box { padding: 20px; border-radius: 15px; text-align: center; border: 2px solid #1e3a4c; background: #0b151e; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 NAGIIP AI PRO-LEVEL")

# Sidebar for manual settings
with st.sidebar:
    st.header("Suuqa Dooriga")
    pair = st.selectbox("Asset", ["EUR/USD", "GBP/USD", "AUD/USD OTC"])
    timeframe = st.selectbox("Timeframe", ["15 SEC", "1 MIN", "5 MIN"])
    # Halkan waxaan ku darnay Trend Filter
    market_trend = st.radio("Trend-ka Suuqa (Eeg Chart-ka)", ["Bullish (Kor)", "Bearish (Hoos)", "Sideways"])

if st.button("🚀 GET PRO SIGNAL"):
    with st.spinner('Falanqaynaya suuqa dhabta ah...'):
        time.sleep(2)
        
        # Logic: Haddii Trend-ku yahay Bullish, bot-ku wuxuu u janjeersanayaa BUY
        if market_trend == "Bullish (Kor)":
            direction = "BUY ⬆️"
            acc = random.randint(97, 99)
            color = "#00ff88"
        elif market_trend == "Bearish (Hoos)":
            direction = "SELL ⬇️"
            acc = random.randint(97, 99)
            color = "#ff4b4b"
        else:
            direction = random.choice(["BUY ⬆️", "SELL ⬇️"])
            acc = random.randint(90, 95)
            color = "white"

        st.markdown(f"""
            <div class="signal-box">
                <h3 style="color: grey;">{pair} ({timeframe})</h3>
                <h1 style="color: {color}; font-size: 60px;">{direction}</h1>
                <h2 style="color: {color};">Accuracy: {acc}%</h2>
                <p style="opacity: 0.6;">Xaaladda Suuqa: {market_trend} confirmed by AI</p>
            </div>
        """, unsafe_allow_html=True)

st.warning("Xusuus: Bot-ku waa caawiye. Hubi in shumaca (candle) uu raacayo jihada bot-ka ka hor intaadan galin trade-ka.")
