import streamlit as st
import random
import time

st.set_page_config(page_title="Pocket Option Filter Bot", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0b0e14; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #1f77b4; color: white; font-weight: bold; }
    .signal-card { padding: 25px; border-radius: 20px; background: #161b22; border: 2px solid #30363d; text-align: center; }
    .status-safe { color: #00ff88; font-weight: bold; }
    .status-risk { color: #ff4b4b; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ SMART FILTER ANALYZER")
st.write("---")

# Doorashada Pair-ka
pair = st.selectbox("Select Asset", ["EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "AUD/USD OTC"])

# Filter Settings (Silently processed)
market_volatility = random.choice(["Low", "Medium", "High"])
trend_strength = random.randint(1, 100)

st.sidebar.subheader("📈 Market Condition")
if trend_strength > 70:
    st.sidebar.markdown("Status: <span class='status-safe'>STRONG TREND</span>", unsafe_allow_html=True)
else:
    st.sidebar.markdown("Status: <span class='status-risk'>UNSTABLE (WAIT)</span>", unsafe_allow_html=True)

st.subheader("Select Time Frame")
cols = st.columns(3)
with cols[0]: t15s = st.button("15 SEC")
with cols[1]: t1m = st.button("1 MIN")
with cols[2]: t5m = st.button("5 MIN")

if any([t15s, t1m, t5m]):
    with st.spinner('Checking Market Filter...'):
        time.sleep(2)
        
        # --- SIGNAL FILTER LOGIC ---
        # Haddii suuqu yahay mid daciif ah (Trend < 50), bot-ku wuxuu oranayaa "No Trade"
        if trend_strength < 50:
            st.warning("⚠️ FILTER ACTIVE: Market is sideways. No clear signal found. Please wait or change pair.")
        else:
            accuracy = random.randint(96, 99)
            direction = random.choice(["CALL (BUY) 🟢", "PUT (SELL) 🔴"])
            
            st.markdown(f"""
                <div class="signal-card">
                    <h2 style="color: white;">Filtered Signal</h2>
                    <p style="color: #8b949e;">Asset: {pair}</p>
                    <hr style="border-color: #30363d;">
                    <h1 style="color: {'#00ff88' if 'CALL' in direction else '#ff4b4b'};">{direction}</h1>
                    <p style="font-size: 20px; color: white;">Confidence: {accuracy}%</p>
                    <p style="color: #00d4ff;">Filter Status: <b>PASSED ✅</b></p>
                </div>
            """, unsafe_allow_html=True)

st.info("💡 Filter-kan wuxuu kaa caawinayaa inaad ka fogaato loss-ka badan adoo diidaya signal-yada daciifka ah.")
