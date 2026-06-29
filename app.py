import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import time
from datetime import datetime

st.set_page_config(
    page_title="Mahad AI - Smart Scanner v6.2",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ PROV MAHAD ULTIMATE AI v6.2 — SMART FILTER")
st.write("Real-Time Multi-Pair Scanner | Kaliya 3-5 Fursadood oo ugu Fiican | OTC + Real Market")

POCKET_OPTION_PAIRS = [
    "AUD/USD", "EUR/USD", "EUR/JPY", "AUD/JPY", "USD/JPY", "EUR/CAD", "USD/CAD",
    "USD/CHF", "EUR/CHF", "AUD/CHF", "CAD/JPY", "CAD/CHF",
    "AUD/CHF OTC", "CAD/JPY OTC", "CHF/JPY OTC", "EUR/JPY OTC",
    "USD/BRL OTC", "USD/CAD OTC", "USD/CNH OTC", "USD/SGD OTC",
    "USD/INR OTC", "USD/ARS OTC", "AUD/USD OTC", "USD/COP OTC",
    "EUR/USD OTC", "EUR/TRY OTC", "USD/MYR OTC", "EUR/CHF OTC",
    "USD/IDR OTC", "USD/JPY OTC", "USD/THB OTC", "USD/MXN OTC"
]

TIMEFRAMES = ["3m", "2m", "1m", "5m"]

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

def fetch_data(ticker_name, tf):
    try:
        fetch_tf = "1m" if tf in ["2m", "3m"] else tf
        period_len = "2d" if fetch_tf == "1m" else "5d"
        df = yf.Ticker(ticker_name).history(period=period_len, interval=fetch_tf)
        if df.empty or len(df) < 30:
            return pd.DataFrame()
        if tf == "2m":
            df = df.resample("2min").agg({
                "Open":"first","High":"max","Low":"min","Close":"last","Volume":"sum"
            }).dropna()
        elif tf == "3m":
            df = df.resample("3min").agg({
                "Open":"first","High":"max","Low":"min","Close":"last","Volume":"sum"
            }).dropna()
        return df.dropna()
    except:
        return pd.DataFrame()

def analyze(df):
    try:
        close  = df["Close"]
        high   = df["High"]
        low    = df["Low"]
        volume = df["Volume"]

        df = df.copy()
        df["RSI"]     = ta.rsi(close, length=14)
        df["RSI_6"]   = ta.rsi(close, length=6)
        df["EMA_9"]   = ta.ema(close, length=9)
        df["EMA_21"]  = ta.ema(close, length=21)
        df["EMA_50"]  = ta.ema(close, length=50)
        df["EMA_200"] = ta.ema(close, length=200)

        macd_df   = ta.macd(close, fast=12, slow=26, signal=9)
        macd_cols = macd_df.columns.tolist()
        df["MACD"]      = macd_df[[c for c in macd_cols if c.startswith("MACD_")][0]]
        df["MACD_HIST"] = macd_df[[c for c in macd_cols if c.startswith("MACDh_")][0]]
        df["MACD_SIG"]  = macd_df[[c for c in macd_cols if c.startswith("MACDs_")][0]]

        bb      = ta.bbands(close, length=20, std=2)
        bb_cols = bb.columns.tolist()
        df["BB_LOW"] = bb[[c for c in bb_cols if c.startswith("BBL")][0]]
        df["BB_UP"]  = bb[[c for c in bb_cols if c.startswith("BBU")][0]]

        stoch      = ta.stoch(high, low, close, k=14, d=3)
        stoch_cols = stoch.columns.tolist()
        df["STOCH_K"] = stoch[stoch_cols[0]]
        df["STOCH_D"] = stoch[stoch_cols[1]]

        adx_df   = ta.adx(high, low, close, length=14)
        adx_cols = adx_df.columns.tolist()
        df["ADX"]    = adx_df[[c for c in adx_cols if c.startswith("ADX_")][0]]
        df["DI_POS"] = adx_df[[c for c in adx_cols if "DMP" in c][0]]
        df["DI_NEG"] = adx_df[[c for c in adx_cols if "DMN" in c][0]]
        df["VOL_MA"] = volume.rolling(20).mean()

        def s(val, d=0):
            return val if not pd.isna(val) else d

        r  = df.iloc[-1]
        r2 = df.iloc[-2]

        price    = r["Close"]
        rsi      = s(r["RSI"],      50)
        rsi6     = s(r["RSI_6"],    50)
        ema9     = s(r["EMA_9"],    price)
        ema21    = s(r["EMA_21"],   price)
        ema50    = s(r["EMA_50"],   price)
        ema200   = s(r["EMA_200"],  price)
        macd     = s(r["MACD"],     0)
        macd_sig = s(r["MACD_SIG"], 0)
        macd_h   = s(r["MACD_HIST"],0)
        macd_h2  = s(r2["MACD_HIST"],0)
        bb_up    = s(r["BB_UP"],    price*1.01)
        bb_low_v = s(r["BB_LOW"],   price*0.99)
        stoch_k  = s(r["STOCH_K"],  50)
        stoch_d  = s(r["STOCH_D"],  50)
        adx      = s(r["ADX"],      0)
        di_pos   = s(r["DI_POS"],   0)
        di_neg   = s(r["DI_NEG"],   0)
        vol      = s(r["Volume"],   0)
        vol_ma   = s(r["VOL_MA"],   1)

        trend_strong = adx > 20
        trend_is_up  = trend_strong and di_pos > di_neg
        trend_is_down= trend_strong and di_neg > di_pos

        cs = 0  # call score
        ps = 0  # put score

        # 1. RSI Logic
        if rsi < 25:
            if trend_is_down: ps += 3
            else: cs += 4
        elif rsi < 35 and not trend_is_down:
            cs += 2
        if rsi > 75:
            if trend_is_up: cs += 3
            else: ps += 4
        elif rsi > 65 and not trend_is_up:
            ps += 2

        # Fast RSI
        if rsi6 < 20 and not trend_is_down: cs += 1
        elif rsi6 > 80 and not trend_is_up:  ps += 1

        # 2. EMA Structure
        if ema9 > ema21 > ema50:   cs += 4
        if ema9 < ema21 < ema50:   ps += 4

        if price > ema200: cs += 1
        else:              ps += 1

        # 3. MACD
        if macd > macd_sig and macd_h > 0:
            cs += 2
            if macd_h > macd_h2: cs += 1
        elif macd < macd_sig and macd_h < 0:
            ps += 2
            if macd_h < macd_h2: ps += 1

        # 4. Bollinger Bands
        if price <= bb_low_v:
            if trend_is_down: ps += 2
            else: cs += 3
        elif price >= bb_up:
            if trend_is_up: cs += 2
            else: ps += 3

        # 5. Stochastic
        if stoch_k < 20 and stoch_d < 20 and not trend_is_down: cs += 2
        if stoch_k > 80 and stoch_d > 80 and not trend_is_up: ps += 2

        # 6. ADX Trend
        if trend_strong:
            if di_pos > di_neg: cs += 4
            else:               ps += 4

        # 7. Volume Filter
        vol_ok = (vol > vol_ma * 0.80) if vol_ma > 0 else False
        is_conflicted = abs(cs - ps) < 4

        if is_conflicted or not vol_ok:
            return "WAIT", 0
        else:
            if cs > ps and cs >= 7: # Waxaan ka dhignay 7 dhibcood si uu signals u helo
                conf = min(60 + int((cs / (cs + (ps * 0.3))) * 35), 95)
                return "CALL", conf
            elif ps > cs and ps >= 7:
                conf = min(60 + int((ps / (ps + (cs * 0.3))) * 35), 95)
                return "PUT", conf
        return "WAIT", 0
    except:
        return "WAIT", 0

# ── SESSION STATE ──────────────────────────────────────────────────────────
if "auto_running" not in st.session_state:
    st.session_state.auto_running = False
if "signals_found" not in st.session_state:
    st.session_state.signals_found = []
if "scan_count" not in st.session_state:
    st.session_state.scan_count = 0

# ── CONTROL BUTTONS ────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    if st.button("▶️ START AUTO SCAN", use_container_width=True, type="primary"):
        st.session_state.auto_running = True
        st.session_state.signals_found = []
        st.session_state.scan_count = 0
with col2:
    if st.button("⏹️ STOP SCAN", use_container_width=True):
        st.session_state.auto_running = False

status_box  = st.empty()
progress_ph = st.empty()

st.markdown("---")
st.subheader("🎯 3-ta Fursadood ee Ugu Fiican Hada (Top Clean Signals)")
results_ph = st.empty()

# ── AUTO SCAN LOOP ─────────────────────────────────────────────────────────
if st.session_state.auto_running:
    status_box.success(f"🟢 AUTO SCAN SOCDA | Wareegga #{st.session_state.scan_count + 1}")

    current_round_signals = []
    total = len(POCKET_OPTION_PAIRS)

    for idx, pair in enumerate(POCKET_OPTION_PAIRS):
        pct = (idx + 1) / total
        progress_ph.progress(pct, text=f"Baarayaa: {pair} ({idx+1}/{total})")

        ticker = get_yahoo_ticker(pair)
        for tf in TIMEFRAMES:
            df = fetch_data(ticker, tf)
            if not df.empty:
                sig, conf = analyze(df)
                if sig in ["CALL", "PUT"]:
                    current_round_signals.append({
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "pair": pair,
                        "tf": tf,
                        "sig": sig,
                        "conf": conf
                    })

    # ── MAX 3 SIGNALS FILTER LOGIC ──
    # Halkan waxaan ku kala saaraynaa kalsoonida ugu sarreysa (Highest Confidence)
    if current_round_signals:
        current_round_signals = sorted(current_round_signals, key=lambda x: x["conf"], reverse=True)
        # Kaliya qaado 3-da ugu sareysa si uusan isticmaaluhu u wareerin
        st.session_state.signals_found = current_round_signals[:3]
    else:
        st.session_state.signals_found = []

    st.session_state.scan_count += 1

    # Render- garee shaxda yar ee kooban
    if not st.session_state.signals_found:
        results_ph.info("Wareeggan wax signal oo adag lama helin. Sug scan-ka xiga 5s ka dib...")
    else:
        rows = []
        for s in st.session_state.signals_found:
            emoji = "🟩 CALL ↑" if s["sig"] == "CALL" else "🟥 PUT ↓"
            rows.append({
                "⏰ Waqti":     s["time"],
                "💱 Pair":      s["pair"],
                "📊 Timeframe": s["tf"],
                "📈 Signal":    emoji,
                "🎯 Kalsooni": f"{s['conf']}%",
                "🏷️ Nooc":      "OTC" if "OTC" in s["pair"] else "Real"
            })
        results_ph.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    time.sleep(5)
    st.rerun()

else:
    status_box.info("White Scanner diyaar — Riix START si aad u bilowdo scan-ka kooban")
    results_ph.info("Kaliya 3-da fursadood ee ugu fiican ayaa halkan ku soo bixi doona mar kasta.")
