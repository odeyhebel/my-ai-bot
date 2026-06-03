import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import google.generativeai as genai
import json

# Habaynta Streamlit UI
st.set_page_config(
    page_title="Mahad AI - Gemini Free Bot", 
    page_icon="⚡", 
    layout="wide"
)

st.title("⚡ PROV MAHAD ULTIMATE GEMINI AI")
st.write("Live Market Scanner via Yahoo Finance & Google Gemini AI (100% Free API)")

POCKET_OPTION_PAIRS = [
    "AUD/USD", "EUR/USD", "EUR/JPY", "AUD/JPY", "USD/JPY", "EUR/CAD", 
    "USD/CAD", "USD/CHF", "EUR/CHF", "AUD/CHF", "CAD/JPY", "CAD/CHF",
    "USD/INR OTC", "USD/SGD OTC", "EUR/USD OTC", "USD/JPY OTC", "GBP/USD OTC"
]

# 🔑 GOOGLE GEMINI API KEY INPUT - SIDEBAR
st.sidebar.header("🔑 Google API Settings")
st.sidebar.write("Geli Google AI Studio API key-gaaga bilaashka ah:")

API_KEY = st.sidebar.text_input(
    label="Google Gemini API Key",
    value="",
    type="password",          
    placeholder="AQ.Ab8RN6...",
    help="Furahaaga ka soo koobiyeeso: aistudio.google.com"
)

if API_KEY:
    st.sidebar.success("✅ Google API Key waa la geliyay")
else:
    st.sidebar.warning("⚠️ Geli API Key-ga si aad nidaamka AI-ga u furto.")

st.sidebar.markdown("---")
st.sidebar.caption("Google Gemini API waa bilaash nidaamka tijaabada (Free Tier).")

col1, col2 = st.columns(2)
with col1:
    selected_pair = st.selectbox("Dooro Pair-ka aad rabto:", POCKET_OPTION_PAIRS)
with col2:
    timeframe = st.selectbox("Timeframe:", ["1m", "2m", "3m", "5m"])

def get_yahoo_ticker(pair_name):
    clean_pair = pair_name.replace(" OTC", "")
    mapping = {
        "AUD/USD": "AUDUSD=X", "EUR/USD": "EURUSD=X", "EUR/JPY": "EURJPY=X",
        "AUD/JPY": "AUDJPY=X", "USD/JPY": "JPY=X",   "EUR/CAD": "EURCAD=X",
        "USD/CAD": "CAD=X",    "USD/CHF": "CHF=X",    "EUR/CHF": "EURCHF=X",
        "AUD/CHF": "AUDCHF=X", "CAD/JPY": "CADJPY=X", "CAD/CHF": "CADCHF=X",
        "USD/INR": "USDINR=X", "USD/SGD": "USDSGD=X"
    }
    return mapping.get(clean_pair, f"{clean_pair.replace('/', '')}=X")

@st.cache_data(ttl=20, show_spinner=False)
def fetch_market_data(ticker_name, tf):
    fetch_tf = "1m" if tf in ["2m", "3m"] else tf
    ticker = yf.Ticker(ticker_name)
    df = ticker.history(period="1d", interval=fetch_tf)

    if df.empty:
        return df

    if tf == "2m":
        df = df.resample('2min').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'})
    elif tf == "3m":
        df = df.resample('3min').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'})

    return df.dropna()

yahoo_ticker = get_yahoo_ticker(selected_pair)

if st.button("⚡ GET LIVE SIGNAL", use_container_width=True):
    if not API_KEY or API_KEY.strip() == "":
        st.error("❌ Fadlan Google API Key-gaaga sidebar-ka ku geli marka hore.")
    else:
        with st.spinner(f"Gemini AI ayaa falanqaynaysa {selected_pair}..."):
            try:
                df = fetch_market_data(yahoo_ticker, timeframe)

                if df.empty or len(df) < 21:
                    st.error("Xog ku filan laga ma helin suuqa hadda. Isku day mar kale.")
                else:
                    df['RSI'] = ta.rsi(df['Close'], length=14)
                    df['EMA_9'] = ta.ema(df['Close'], length=9)
                    df['EMA_21'] = ta.ema(df['Close'], length=21)

                    current_price = df['Close'].iloc[-1]
                    last_rsi = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50
                    last_ema9 = df['EMA_9'].iloc[-1]
                    last_ema21 = df['EMA_21'].iloc[-1]

                    prompt = f"""
You are an expert binary options trading bot. Analyze this market data:
Asset: {selected_pair}
Timeframe: {timeframe}
Current Price: {current_price:.5f}
RSI (14): {last_rsi:.2f}
EMA 9: {last_ema9:.5f}
EMA 21: {last_ema21:.5f}

Rules:
- Give CALL if RSI < 40 and EMA_9 > EMA_21
- Give PUT if RSI > 60 and EMA_9 < EMA_21
- Otherwise give WAIT

Respond ONLY with raw JSON format, no markdown blocks, no ```json ``` fences:
{{"signal": "CALL/PUT/WAIT", "confidence": 85, "reason": "Short analytical reason in Somali language"}}
"""

                    # 🟩 QAABKA RAGMIGA AH EE GOOGLE SDK LIBRARY
                    genai.configure(api_key=API_KEY.strip())
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    
                    response = model.generate_content(prompt)
                    ai_response = response.text.strip()
                    
                    # Nadiifinta calaamadaha markdown-ka haddii ay jiraan
                    ai_response = ai_response.replace("```json", "").replace("```", "").strip()
                    result = json.loads(ai_response)

                    st.success("Signal-kii bilaashka ahaa ee Gemini waa diyaar!")
                    st.metric(label=f"Qiimaha Hadda ({selected_pair})", value=f"{current_price:.5f}")

                    signal = result['signal']
                    if signal == "CALL":
                        st.subheader(f"🟩 SIGNAL: {signal}")
                    elif signal == "PUT":
                        st.subheader(f"🟥 SIGNAL: {signal}")
                    else:
                        st.subheader(f"🟨 SIGNAL: {signal}")

                    st.write(f"**Kalsooni:** {result['confidence']}%")
                    st.write(f"**Sababta:** {result['reason']}")

                    with st.expander("📊 Xogta Indicators-ka"):
                        st.write(f"RSI: {last_rsi:.2f} | EMA 9: {last_ema9:.5f} | EMA 21: {last_ema21:.5f}")

            except Exception as e:
                st.error(f"Cilad: {str(e)}")
