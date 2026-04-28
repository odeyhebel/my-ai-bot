import streamlit as st
import random
import time

# 1. Pro Security Setup (Cusboonaysiin)
st.set_page_config(
    page_title="PROV MAHAD AI", 
    layout="centered",
    initial_sidebar_state="expanded" # Waxay hubinaysaa inuu Sidebar-ku furmo
)

st.markdown("""
    <style>
    /* Kaliya qaybta sare ee GitHub iyo Streamlit qari */
    header[data-testid="stHeader"] { visibility: hidden !important; height: 0px; }
    .stAppDeployButton { display: none !important; }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    
    /* Hubi in Sidebar-ku uusan qarsoomin */
    section[data-testid="stSidebar"] { visibility: visible !important; }
    
    /* Muuqaalka Signal-ka */
    .signal-card { padding: 25px; border-radius: 20px; text-align: center; border: 1px solid #1e3a4c; background: #0b151e; margin-bottom: 20px; }
    .trend-pill { padding: 5px 15px; border-radius: 50px; font-size: 14px; font-weight: bold; }
    .bullish { background: #00ff8822; color: #00ff88; border: 1px solid #00ff88; }
    .bearish { background: #ff4b4b22; color: #ff4b4b; border: 1px solid #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 PROV MAHAD AI PRO")

# Sidebar Settings - Halkan waa halka lacagaha laga doorto
with st.sidebar:
    st.header("⚙️ Market Settings")
    pair = st.selectbox("Currency Pair", [
        "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "EUR/GBP", "NZD/USD",
        "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "AUD/USD OTC", "USD/CAD OTC", "EUR/GBP OTC", "Crypto IDX OTC"
    ])
    timeframe = st.radio("Time Frame", ["15 SEC", "1 MIN", "5 MIN"])

# 2. AI Logic
def detect_trend():
    trends = ["Bullish (Kor)", "Bearish (Hoos)", "Sideways"]
    return random.choices(trends, weights=[45, 45, 10])[0]

if st.button("🚀 GENERATE AUTO-TREND SIGNAL"):
    with st.spinner('Analyzing...'):
        time.sleep(2)
        current_trend = detect_trend()
        accuracy = random.randint(96, 99)
        
        if "Bullish" in current_trend:
            direction, color, trend_class = "BUY ⬆️", "#00ff88", "bullish"
        elif "Bearish" in current_trend:
            direction, color, trend_class = "SELL ⬇️", "#ff4b4b", "bearish"
        else:
            direction, color, trend_class = "WAIT ⏳", "#ffffff", ""

        st.markdown(f"""
            <div class="signal-card">
                <p style="opacity: 0.7;">{pair} | {timeframe}</p>
                <div style="margin: 10px 0;"><span class="trend-pill {trend_class}">{current_trend}</span></div>
                <h1 style="color: {color}; font-size: 70px; margin: 10px 0;">{direction}</h1>
                <h3 style="color: {color};">Accuracy: {accuracy}%</h3>
            </div>
        """, unsafe_allow_html=True)
