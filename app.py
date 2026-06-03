import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import requests
import json

# 1. Habaynta Streamlit UI (Halkan baa ciladu ku jirtay, hadda waa sax)
st.set_page_config(
    page_title="Mahad AI - Live Signal Bot", 
    page_icon="⚡", 
    layout="wide"  # "wide" ama "centered" kaliya ayaa sax ah
)

st.title("⚡ PROV MAHAD ULTIMATE AI")
st.write("Live Market Scanner via Yahoo Finance & AI Analysis")

# Dhammaan lacagihii aad rabtay
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

# Yahoo Finance waxay u baahan tahay qaab ka duwan 2m ama 3m (1m, 5m ayaa ugu haboon)
timeframe = st.selectbox("Timeframe:", ["1m", "5m", "15m", "1h"])

# Geli API Key-gaaga Anthropic rasmiga ah
API_KEY = "HALKAN_GELI_API_KEY_GAAGA"

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

yahoo_ticker = get_yahoo_ticker(selected_pair)

if st.button("GET LIVE SIGNAL"):
    with st.spinner(f"La xiriiraya suuqa dhabta ah ee {selected_pair}..."):
        try:
            ticker = yf.Ticker(yahoo_ticker)
            df = ticker.history(period="1d", interval=timeframe)
            
            if df.empty:
                st.error(f"Xogta lacagta {selected_pair} hadda lagama helid karo Yahoo Finance. Hubi in suuqu furanyahay ama isku day pair kale.")
            else:
                # Xisaabi Tilmaamayaasha Farsamada (Hadda pandas_ta waa shaqaynaysaa)
                df['RSI'] = ta.rsi(df['Close'], length=14)
                df['EMA_9'] = ta.ema(df['Close'], length=9)
                df['EMA_21'] = ta.ema(df['Close'], length=21)
                
                # Qaado xogta ugu dambeysay
                current_price = df['Close'].iloc[-1]
                last_rsi = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50
                last_ema9 = df['EMA_9'].iloc[-1]
                last_ema21 = df['EMA_21'].iloc[-1]
                
                # Prompt-ka AI-ga
                prompt = f"""
                You are an expert binary options trading bot. Analyze the following LIVE market data:
                Asset: {selected_pair}
                Current Price: {current_price:.5f}
                RSI (14): {last_rsi:.2f}
                EMA 9: {last_ema9:.5f}
                EMA 21: {last_ema21:.5f}
                
                Scoring Rules:
                - Give CALL if RSI < 40 and EMA_9 > EMA_21
                - Give PUT if RSI > 60 and EMA_9 < EMA_21
                - Give WAIT if signals are mixed.
                
                Respond ONLY with JSON format, no markdown:
                {{"signal": "CALL/PUT/WAIT", "confidence": 0-100, "reason": "Short reason in Somali"}}
                """
                
                # U dir API-ga Claude
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
                    
                    st.success("Signal-kii waa diyaar!")
                    st.metric(label=f"Qiimaha Hadda ({selected_pair})", value=f"{current_price:.5f}")
                    
                    if result['signal'] == "CALL":
                        st.subheader(f"🟩 SIGNAL: {result['signal']}")
                    elif result['signal'] == "PUT":
                        st.subheader(f"🟥 SIGNAL: {result['signal']}")
                    else:
                        st.subheader(f"🟨 SIGNAL: {result['signal']}")
                        
                    st.write(f"**Kalsooni:** {result['confidence']}%")
                    st.write(f"**Sababta AI-ga:** {result['reason']}")
                else:
                    st.error(f"AI Server Error: {response.status_code}. Hubi furahaaga API Key rasmiga ah.")
                    
        except Exception as e:
            st.error(f"Cilad koodhka dhexdiisa ah: {str(e)}")
