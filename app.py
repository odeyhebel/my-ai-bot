import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import time
from datetime import datetime

st.set_page_config(
    page_title="Mahad AI - Auto Scanner v6",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ PROV MAHAD ULTIMATE AI v6")
st.write("Real-Time Multi-Pair & Multi-Timeframe Auto Scanner (OTC + Real Market)")

POCKET_OPTION_PAIRS = [
    "AUD/USD", "EUR/USD", "EUR/JPY", "AUD/JPY", "USD/JPY", "EUR/CAD", "USD/CAD",
    "USD/CHF", "EUR/CHF", "AUD/CHF", "CAD/JPY", "CAD/CHF", "AED/CNY OTC",
    "AUD/CHF OTC", "CAD/JPY OTC", "CHF/JPY OTC", "CHF/NOK OTC", "EUR/HUF OTC",
    "EUR/JPY OTC", "NGN/USD OTC", "QAR/CNY OTC", "UAH/USD OTC", "USD/BDT OTC",
    "USD/BRL OTC", "USD/CAD OTC", "USD/CLP OTC", "USD/CNH OTC", "USD/PKR OTC",
    "USD/SGD OTC", "YER/USD OTC", "USD/INR OTC", "KES/USD OTC", "USD/ARS OTC",
    "AUD/USD OTC", "USD/COP OTC", "EUR/USD OTC", "EUR/TRY OTC", "USD/MYR OTC",
    "USD/VND OTC", "EUR/CHF OTC", "LBP/USD OTC", "MAD/USD OTC", "EUR/RUB OTC",
    "OMR/CNY OTC", "SAR/CNY OTC", "USD/IDR OTC", "USD/JPY OTC", "USD/THB OTC",
    "TND/USD OTC", "USD/MXN OTC"
]

TIMEFRAMES = ["1m", "2m", "3m", "5m"]

def get_yahoo_ticker(pair_name):
    clean_pair = pair_name.replace(" OTC", "")
    mapping = {
        "AUD/USD": "AUDUSD=X", "EUR/USD": "EURUSD=X", "EUR/JPY": "EURJPY=X",
        "AUD/JPY": "AUDJPY=X", "USD/JPY": "JPY=X",    "EUR/CAD": "EURCAD=X",
        "USD/CAD": "CAD=X",    "USD/CHF": "CHF=X",     "EUR/CHF": "EURCHF=X",
        "AUD/CHF": "AUDCHF=X", "CAD/JPY": "CADJPY=X",  "CAD/CHF": "CADCHF=X",
        "USD/INR": "USDINR=X", "USD/SGD": "USDSGD=X",  "USD/BRL": "USDBRL=X",
        "USD/PKR": "USDPKR=X", "USD/THB": "USDTHB=X",  "USD/MXN": "USDMXN=X",
        "CHF/JPY": "CHFJPY=X", "EUR/TRY": "EURTRY=X",  "USD/CNH": "USDCNH=X",
        "USD/IDR": "USDIDR=X", "USD/MYR": "USDMYR=X",  "USD/ARS": "USDARS=X",
        "USD/COP": "USDCOP=X", "USD/CLP": "USDCLP=X",
    }
    if clean_pair in mapping:
        return mapping[clean_pair]
    parts = clean_pair.split("/")
    if len(parts) == 2:
        return f"{parts[0]}{parts[1]}=X"
    return "EURUSD=X"

def fetch_market_data_silent(ticker_name, tf):
    try:
        fetch_tf = "1m" if tf in ["2m", "3m"] else tf
        ticker = yf.Ticker(ticker_name)
        period_len = "2d" if fetch_tf == "1m" else "5d"
        df = ticker.history(period=period_len, interval=fetch_tf)
        if df.empty or len(df) < 30:
            return pd.DataFrame()
        if tf == "2m":
            df = df.resample("2min").agg({
                "Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"
            }).dropna()
        elif tf == "3m":
            df = df.resample("3min").agg({
                "Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"
            }).dropna()
        return df.dropna()
    except:
        return pd.DataFrame()

def analyze_signal_silent(df):
    close  = df["Close"]
    high   = df["High"]
    low    = df["Low"]
    volume = df["Volume"]

    df["RSI"]     = ta.rsi(close, length=14)
    df["EMA_9"]   = ta.ema(close, length=9)
    df["EMA_21"]  = ta.ema(close, length=21)
    df["EMA_50"]  = ta.ema(close, length=50)
    
    adx_df   = ta.adx(high, low, close, length=14)
    adx_cols = adx_df.columns.tolist()
    df["ADX"]    = adx_df[[c for c in adx_cols if c.startswith("ADX_")][0]]
    df["DI_POS"] = adx_df[[c for c in adx_cols if "DMP" in c][0]]
    df["DI_NEG"] = adx_df[[c for c in adx_cols if "DMN" in c][0]]

    r = df.iloc[-1]
    price  = r["Close"]
    rsi    = r["RSI"] if not pd.isna(r["RSI"]) else 50
    ema9   = r["EMA_9"] if not pd.isna(r["EMA_9"]) else price
    ema21  = r["EMA_21"] if not pd.isna(r["EMA_21"]) else price
    ema50  = r["EMA_50"] if not pd.isna(r["EMA_50"]) else price
    adx    = r["ADX"] if not pd.isna(r["ADX"]) else 0
    di_pos = r["DI_POS"] if not pd.isna(r["DI_POS"]) else 0
    di_neg = r["DI_NEG"] if not pd.isna(r["DI_NEG"]) else 0

    trend_strong = adx > 22
    trend_is_up  = trend_strong and di_pos > di_neg
    trend_is_down= trend_strong and di_neg > di_pos

    call_score = 0
    put_score  = 0

    if rsi < 25:
        if trend_is_down: put_score += 3
        else: call_score += 4
    elif rsi > 75:
        if trend_is_up: call_score += 3
        else: put_score += 4

    if ema9 > ema21 > ema50: call_score += 4
    if ema9 < ema21 < ema50: put_score += 4

    if trend_strong:
        if di_pos > di_neg: call_score += 4
        else: put_score += 4

    is_conflicted = abs(call_score - put_score) < 4

    if is_conflicted:
        return "WAIT", 0
    else:
        if call_score > put_score and call_score >= 8:
            confidence = min(60 + int((call_score / (call_score + (put_score*0.3))) * 35), 95)
            return "CALL", confidence
        elif put_score > call_score and put_score >= 8:
            confidence = min(60 + int((put_score / (put_score + (call_score*0.3))) * 35), 95)
            return "PUT", confidence
    return "WAIT", 0

# ── SCANNER BUTTON ──
st.subheader("🔍 Scan- garee Dhamaan Fursadaha Suuqa")
st.write("Markaad badanka hoose riixdo, bot-ku wuxuu baari doonaa dhammaan lacagaha iyo waqtiyada kala duwan si uu u helo fursad furan hadda.")

if st.button("🚀 RUN AUTOMATIC SCANNER", use_container_width=True):
    found_signals = []
    
    progress_text = st.empty()
    progress_bar = st.progress(0)
    
    total_scans = len(POCKET_OPTION_PAIRS)
    
    for idx, pair in enumerate(POCKET_OPTION_PAIRS):
        progress_text.text(f"Baarayaa: {pair} ({idx+1}/{total_scans})... ⏳")
        progress_bar.progress((idx + 1) / total_scans)
        
        ticker = get_yahoo_ticker(pair)
        
        # Isku mar u baar dhamaan afarta timeframe ee pair-kan
        for tf in TIMEFRAMES:
            df = fetch_market_data_silent(ticker, tf)
            if not df.empty:
                sig, con = analyze_signal_silent(df)
                if sig in ["CALL", "PUT"] and con >= 80: # Kaliya signals-ka adag soo saar
                    found_signals.append({
                        "Pair": pair,
                        "Timeframe": tf,
                        "Signal Direction": "🟩 CALL" if sig == "CALL" else "🟥 PUT",
                        "Confidence": f"{con}%",
                        "Time Found": datetime.now().strftime("%H:%M:%S")
                    })
                    
    progress_text.text("Scan-kii waa dhammaaday! ✅")
    
    st.markdown("---")
    st.subheader("🎯 Fursadaha Furan Hadda (Signals Detected)")
    
    if len(found_signals) > 0:
        # U beddel shaxan (Table) qurux badan si sahal loogu akhriyo
        df_signals = pd.DataFrame(found_signals)
        
        # Habayn midabayn UI ah
        st.dataframe(df_signals, use_container_width=True, hide_index=True)
        
        st.success(f"Waxaa la helay **{len(found_signals)}** fursadood oo aad u adag oo aad hadda Pocket Option ka gali karto!")
    else:
        st.warning("Hadda ma jiraan fursadaha buuxiyey shuruudihii adkaa ee v6. Sug dhowr daqiiqo ka dibna mar kale run garee scanner-ka.")
