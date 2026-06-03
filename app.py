import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import requests
import json

# 1. Habaynta Streamlit UI
st.set_page_config(
    page_title="Mahad AI - Live Signal Bot", 
    page_icon="⚡", 
    layout="wide"
)

st.title("⚡ PROV MAHAD ULTIMATE AI")
st.write("Live Market Scanner via Yahoo Finance & AI Analysis (Taageeraya 2m & 3m)")

POCKET_OPTION_PAIRS = [
    "AUD/USD", "EUR/USD", "EUR/JPY", "AUD/JPY", "USD/JPY", "EUR/CAD", 
    "USD/CAD", "USD/CHF", "EUR/CHF", "AUD/CHF", "CAD/JPY", "CAD/CHF",
    "AED/CNY OTC", "AUD/CHF OTC", "CAD/JPY OTC", "CHF/JPY OTC", "CHF/NOK OTC",
    "EUR/HUF OTC", "EUR/JPY OTC", "NGN/USD OTC", "QAR/CNY OTC", "UAH/USD OTC",
    "USD/BDT OTC", "USD/BRL OTC", "USD/CAD OTC", "USD/CLP OTC", "USD/CNH OTC",
    "USD/PKR OTC", "USD/SGD OTC", "YER/USD OTC", "USD/INR OTC", "KES/USD OTC",
    "USD/ARS OTC", "AUD/USD OTC", "USD/COP OTC", "EUR/USD OTC", "EUR/TRY OTC",
    "USD/MYR OTC", "USD/VND OTC", "EUR/CHF OTC", "LBP/USD OTC", "MAD/USD OTC",
    "EUR/RUB OTC", "OMR/CNY OTC", "SAR/CNY OTC", "USD/IDR OTC", "USD/JPY OTC",
    "USD/THB OTC", "TND/USD OTC", "USD/MXN OTC"
]

selected_pair = st.selectbox("Dooro Pair-ka aad rabto:", POCKET_OPTION_PAIRS)

# Diyaar waxaa kuu ah 1m, 2m, 3m, iyo 5m!
timeframe = st.selectbox("Timeframe:", ["1m", "2m", "3m", "5m"])

# ⚠️ MUHIIM: HALKAN DHEX GELI FURahaaga ANTHROPIC EE RASMIGA AH
API_KEY = "sk-ant-at03-XOGTA_FURAHAGA_HALKAN_GELI"

def get_yahoo_ticker(pair_name):
    clean_pair = pair_name.replace(" OTC", "")
    mapping = {
        "AUD/USD": "AUDUSD=X", "EUR/USD": "EURUSD=X", "EUR/JPY": "EURJPY=X",
        "AUD/JPY": "AUDJPY=X", "USD/JPY": "JPY=X", "EUR/CAD": "EURCAD=X",
        "USD/CAD": "CAD=X", "USD/CHF": "CHF=X", "EUR/CHF": "EURCHF=X",
        "AUD/CHF": "AUDCHF=X", "CAD/JPY": "CADJPY=X", "CAD/CHF": "CADCHF=X",
        "USD/INR": "USDINR=X", "USD/SGD": "USDSGD=X", "USD/BRL": "USDBRL=X",
        "USD/PKR": "USDPKR=X", "USD/THB": "USDTHB=X", "USD/MXN": "USDMXN=X"
    }
    if clean_pair in mapping:
        return mapping[clean_pair]
    parts = clean_pair.split("/")
    if len(parts) == 2:
        return f"{parts[0]}{parts[1]}=X"
    return "EURUSD=X"

@st.cache_data(ttl=30, show_spinner=False)
def fetch_market_data(ticker_name, tf):
    fetch_tf = "1m" if tf in ["2m", "3m"] else tf
    ticker = yf.Ticker(ticker_name)
    df = ticker.history(period="1d", interval=fetch_tf)
    
    if df.empty:
        return df
        
    # Isku dhex dhiib xogta si loo helo 2m iyo 3m
    if tf == "2m":
        df = df.resample('2min').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'})
    elif tf == "3m":
        df = df.resample('3min').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'})
        
    return df.dropna()

yahoo_ticker = get_yahoo_ticker(selected_pair)

if st.button("GET LIVE SIGNAL"):
    if API_KEY == "sk-ant-at03-XOGTA_FURAHAGA_HALKAN_GELI" or API_KEY == "":
        st.warning("Fadlan koodhka dhexdiisa ku qor API Key-gaaga rasmiga ah ka hor inta aadan riixin badanka.")
    else:
        with st.spinner(f"La xiriiraya suuqa dhabta ah ee {selected_pair}..."):
            try:
                df = fetch_market_data(yahoo_ticker, timeframe)
                
                if df.empty or len(df) < 21:
                    st.error(f"Xog ku filan laga ma helin {selected_pair} hadda. Isku day mar kale ama Pair kale.")
                else:
                    df['RSI'] = ta.rsi(df['Close'], length=14)
                    df['EMA_9'] = ta.ema(df['Close'], length=9)
                    df['EMA_21'] = ta.ema(df['Close'], length=21)
                    
                    current_price = df['Close'].iloc[-1]
                    last_rsi = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50
                    last_ema9 = df['EMA_9'].iloc[-1]
                    last_ema21 = df['EMA_21'].iloc[-1]
                    
                    prompt = f"""
                    You are an expert binary options trading bot. Analyze the following LIVE market data:
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
                    
                    Respond ONLY with JSON format, no markdown:
                    {{"signal": "CALL/PUT/WAIT", "confidence": 0-100, "reason": "Short reason in Somali language"}}
                    """
                    
                    headers = {
                        "x-api-key": API_KEY,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    }
                    data = {
                        "model": "claude-3-5-sonnet-20241022",
                        "max_tokens": 150,
                        "messages": [{"role": "user", "content": prompt}]
                    }
                    
                    response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
                    
                    if response.status_code == 200:
                        ai_response = response.json()['content'][0]['text']
                        result = json.loads(ai_response)
                        
                        st.success(f"Signal-kii {timeframe} waa diyaar!")
                        st.metric(label=f"Qiimaha Hadda ({selected_pair})", value=f"{current_price:.5f}")
                        
                        if result['signal'] == "CALL":
                            st.subheader(f"🟩 SIGNAL: {result['signal']}")
                        elif result['signal'] == "PUT":
                            st.subheader(f"🟥 SIGNAL: {result['signal']}")
                        else:
                            st.subheader(f"🟨 SIGNAL: {result['signal']}")
                            
                        st.write(f"**Kalsooni:** {result['confidence']}%")
                        st.write(f"**Sababta:** {result['reason']}")
                    else:
                        st.error(f"AI Server Error: {response.status_code}. Hubi in API Key-gu sax yahay ama uu leeyahay hanti (credits).")
                        
            except Exception as e:
                if "Too Many Requests" in str(e) or "429" in str(e):
                    st.error("Yahoo Finance ayaa mashquul ah. Fadlan sug 1 daqiiqo dibna u riix badanka.")
                else:
                    st.error(f"Cilad koodhka dhexdiisa ah: {str(e)}")
