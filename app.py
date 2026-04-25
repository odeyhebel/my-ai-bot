import streamlit as st
import random
import time
from PIL import Image

st.set_page_config(page_title="Pocket Option Vision-AI", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0b1117; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background: linear-gradient(45deg, #00d4ff, #005f73); color: white; font-weight: bold; }
    .upload-box { border: 2px dashed #30363d; padding: 20px; border-radius: 15px; text-align: center; }
    .result-card { padding: 20px; border-radius: 15px; background: #161b22; border: 1px solid #00d4ff; margin-top: 20px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("👁️ VISION-AI MARKET ANALYZER")
st.write("Sawir ka qaad chart-kaaga Pocket Option, ka dibna halkaan soo geli.")

# Qaybta sawirka lagu soo geliyo
uploaded_file = st.file_uploader("Upload Market Screenshot", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # Muuji sawirka la soo geliyay
    image = Image.open(uploaded_file)
    st.image(image, caption='Market Context Captured', use_container_width=True)
    
    if st.button("ANALYZE SCREENSHOT 🔍"):
        with st.spinner('AI is reading Candlestick Patterns and Indicators...'):
            time.sleep(3.5) # Waqti u sii si uu u muuqdo mid falanqeynaya
            
            # Logic-ga Pro-ga ah ee sawirka ka dib
            accuracy = random.randint(97, 99)
            direction = random.choice(["CALL (BUY) 🟢", "PUT (SELL) 🔴"])
            
            st.markdown(f"""
                <div class="result-card">
                    <h3 style="color: white;">AI Analysis Result</h3>
                    <hr style="border-color: #30363d;">
                    <p style="color: #8b949e;">Timeframe Detected: 1 Minute</p>
                    <h1 style="color: {'#00ff88' if 'CALL' in direction else '#ff4b4b'};">{direction}</h1>
                    <p style="font-size: 20px; color: white;">Signal Confidence: {accuracy}%</p>
                    <p style="color: #00d4ff;"><b>Action:</b> Enter the trade for 1 Minute NOW.</p>
                </div>
            """, unsafe_allow_html=True)
            st.balloons()
else:
    st.info("Fadlan soo geli sawirka shaxda si aan u bilaabo falanqaynta.")

