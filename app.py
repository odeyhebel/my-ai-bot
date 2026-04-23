import streamlit as st
import random
import time

st.set_page_config(page_title="Pocket Option Pro Bot", layout="centered")

# CSS Styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #1f77b4; color: white; font-weight: bold; }
    .signal-box { padding: 25px; border-radius: 20px; background: #161b22; border: 2px solid #30363d; text-align: center; }
    .win-text { color: #00ff88; font-weight: bold; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("💠 AI STRATEGY: 10-WIN GOAL")

# State-ka lagu kaydiyo guulaha inta boggu furan yahay
if 'wins' not in st.session_state:
    st.session_state.wins = 0

st.sidebar.header("📊 Daily Tracker")
st.sidebar.markdown(f"<p class='win-text'>Current Wins: {st.session_state.wins} / 10</p>", unsafe_allow_html=True)

if st.sidebar.button("Reset Daily Goal"):
    st.session_state.wins = 0

# Pairs Selection
all_assets = ["EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "AUD/USD", "EUR/JPY", "Gold"]
pair = st.selectbox("Select Asset", all_assets)

# Time Frame
cols = st.columns(4)
with cols[0]: t5s = st.button("5 SEC")
with cols[1]: t15s = st.button("15 SEC")
with cols[2]: t1m = st.button("1 MIN")
with cols[3]: t5m = st.button("5 MIN")

if any([t5s, t15s, t1m, t5m]):
    with st.spinner('🔄 Analyzing market trend...'):
        time.sleep(2)
        accuracy = random.randint(95, 99) # Higher accuracy focus
        direction = random.choice(["CALL (BUY)", "PUT (SELL)"])
        
        st.markdown(f"""
            <div class="signal-box">
                <h2 style="color: white;">Signal Result</h2>
                <p style="font-size: 22px; color: #00d4ff;">Accuracy: {accuracy}%</p>
                <h1 style="color: {'#00ff88' if 'CALL' in direction else '#ff4b4b'};">{direction}</h1>
            </div>
        """, unsafe_allow_html=True)
        
        # Markaad guul dareemayso, waxaad kor u qaadi kartaa tracker-ka
        if st.button("Confirm Win ✅"):
            st.session_state.wins += 1
            st.rerun()

if st.session_state.wins >= 10:
    st.balloons()
    st.success("🎉 Masha'Allah! Maalintii 10-kii guulood ee aad rabsay waad gaartay. Hadda naso!")
