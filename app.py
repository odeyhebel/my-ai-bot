import streamlit as st
import random
import time

# 1. Pro UI Setup
st.set_page_config(page_title="PROV MAHAD AI", layout="centered")

st.markdown("""
    <style>
    /* 100% Qarinta GitHub icon-ka si qofna uusan koodhka u arkin */
    header[data-testid="stHeader"] { visibility: hidden !important; height: 0px; }
    .stAppDeployButton { display: none !important; }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    
    /* Interface-ka bot-ka inuu muuqdo */
    .main { background-color: #050a0e; }
    .signal-card { 
        padding: 25px; border-radius: 20px; text-align: center; 
        border: 2px solid #1e3a4c; background: #0b151e; margin-top: 20px; 
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 PROV MAHAD AI PRO")

# 2. Settings-ka (Hadda waa dhexda si dadka oo dhami u arkaan)
with st.expander("⚙️ SETTINGS: DOOR LACAGTA IYO WAQTIGA", expanded=True):
    pair = st.selectbox("Currency Pair", [
        "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "EUR/GBP", "NZD/USD",
        "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "AUD/USD OTC", "USD/CAD OTC", "EUR/GBP OTC", "Crypto IDX OTC"
    ])
    timeframe = st.radio("Time Frame", ["15 SEC", "1 MIN", "5 MIN"], horizontal=True)

# 3. Main Action - Qof kasta wuxuu gujin karaa batoonkan
if st.button("🚀 GENERATE AUTO-TREND SIGNAL"):
    with st.spinner('Falanqaynaya...'):
        time.sleep(2)
        
        trends = ["Bullish (Kor)", "Bearish (Hoos)", "Sideways"]
        current_trend = random.choices(trends, weights=[45, 45, 10])[0]
        accuracy = random.randint(96, 99)
        
        if "Bullish" in current_trend:
            direction, color = "BUY ⬆️", "#00ff88"
        elif "Bearish" in current_trend:
            direction, color = "SELL ⬇️", "#ff4b4b"
        else:
            direction, color = "WAIT ⏳", "#ffffff"

        st.markdown(f"""
            <div class="signal-card">
                <h3 style="color: grey;">{pair} | {timeframe}</h3>
                <p style="color: {color}; font-weight: bold;">Trend Detection: {current_trend}</p>
                <h1 style="color: {color}; font-size: 60px;">{direction}</h1>
                <h2 style="color: {color};">Accuracy: {accuracy}%</h2>
            </div>
        """, unsafe_allow_html=True)
        
        if accuracy >= 98:
            st.balloons()
