import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# 1. Habaynta Streamlit UI
st.set_page_config(
    page_title="Mahad AI - Free Live Bot", 
    page_icon="⚡", 
    layout="wide"
)

st.title("⚡ PROV MAHAD FREE AI BOT")
st.write("Live Market Scanner (No API Key Required - 100% Free)")

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
timeframe = st.selectbox("Timeframe:", ["1m", "2m", "3m", "5m"])

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
        
    if tf == "2m":
        df = df.resample('2min').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'})
    elif tf == "3m":
        df = df.resample('3min').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'})
        
    return df.dropna()

yahoo_ticker = get_yahoo_ticker(selected_pair)

if st.button("GET LIVE SIGNAL"):
    with st.spinner(f"La xiriiraya suuqa dhabta ah ee {selected_pair}..."):
        try:
            df = fetch_market_data(yahoo_ticker, timeframe)
            
            if df.empty or len(df) < 21:
                st.error(f"Xog ku filan laga ma helin {selected_pair} hadda. Isku day mar kale.")
            else:
                # Xisaabi Indicators-ka
                df['RSI'] = ta.rsi(df['Close'], length=14)
                df['EMA_9'] = ta.ema(df['Close'], length=9)
                df['EMA_21'] = ta.ema(df['Close'], length=21)
                
                current_price = df['Close'].iloc[-1]
                last_rsi = df['RSI'].iloc[-1]
                last_ema9 = df['EMA_9'].iloc[-1]
                last_ema21 = df['EMA_21'].iloc[-1]
                
                # --- XEERKA KALA DOORASHADA CODSIGA (FREE AUTO-ALGORITHM) ---
                signal = "WAIT"
                confidence = 50
                reason = "Suuqu ma laha jiho cad hadda. Sug inta tilmaamayaashu isku raacayaan."
                
                if last_rsi < 40 and last_ema9 > last_ema21:
                    signal = "CALL"
                    confidence = 85
                    reason = f"RSI ayaa muujisay in suuqu aad u hooseeyo ({last_rsi:.1f}), isla markaana EMA 9 ayaa kor u jartay EMA 21 oo muujisay kor u kac."
                elif last_rsi > 60 and last_ema9 < last_ema21:
                    signal = "PUT"
                    confidence = 85
                    reason = f"RSI ayaa muujisay in suuqu aad u sarreeyo ({last_rsi:.1f}), isla markaana EMA 9 ayaa hoos u jartay EMA 21 oo muujisay hoos u dhac."
                
                # Soo bandhig Natiijada
                st.success(f"Falanqayntii {timeframe} waa diyaar!")
                st.metric(label=f"Qiimaha Hadda ({selected_pair})", value=f"{current_price:.5f}")
                
                # Muujinta Signal-ka rasmiga ah
                if signal == "CALL":
                    st.subheader(f"🟩 SIGNAL: {signal}")
                elif signal == "PUT":
                    st.subheader(f"🟥 SIGNAL: {signal}")
                else:
                    st.subheader(f"🟨 SIGNAL: {signal}")
                    
                st.write(f"**Kalsooni:** {confidence}%")
                st.write(f"**Sababta farsamo:** {reason}")
                
                # Tus qiimaha tilmaamayaasha si aad Pocket Option ugu dhex hubiso
                st.info(f"Xogta lafagurka: RSI: {last_rsi:.2f} | EMA 9: {last_ema9:.5f} | EMA 21: {last_ema21:.5f}")
                        
        except Exception as e:
            if "Too Many Requests" in str(e) or "429" in str(e):
                st.error("Yahoo Finance ayaa xoogaa mashquushay. Fadlan sug 1 daqiiqo dibna u riix badanka.")
            else:
                st.error(f"Cilad: {str(e)}")
