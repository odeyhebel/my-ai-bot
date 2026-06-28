import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import time

st.set_page_config(
    page_title="Mahad AI - Live Signal Bot v5",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ PROV MAHAD ULTIMATE AI v5")
st.write("High Accuracy Scanner | Trend-Following + Volume Penalty + Conflict Protection")

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

col1, col2 = st.columns(2)
with col1:
    selected_pair = st.selectbox("Dooro Pair-ka:", POCKET_OPTION_PAIRS)
with col2:
    timeframe = st.selectbox("Timeframe:", ["1m", "2m", "3m", "5m"])

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

@st.cache_data(ttl=60)
def fetch_market_data(ticker_name, tf):
    fetch_tf = "1m" if tf in ["2m", "3m"] else tf
    ticker = yf.Ticker(ticker_name)
    period_len = "2d" if fetch_tf == "1m" else "5d"
    df = ticker.history(period=period_len, interval=fetch_tf)
    if df.empty:
        return df
    if tf == "2m":
        df = df.resample("2min").agg({
            "Open": "first", "High": "max",
            "Low": "min", "Close": "last", "Volume": "sum"
        }).dropna()
    elif tf == "3m":
        df = df.resample("3min").agg({
            "Open": "first", "High": "max",
            "Low": "min", "Close": "last", "Volume": "sum"
        }).dropna()
    return df.dropna()

def get_support_resistance(df, lookback=50):
    recent     = df.tail(lookback)
    resistance = recent["High"].max()
    support    = recent["Low"].min()
    pivot      = (resistance + support + recent["Close"].iloc[-1]) / 3
    r1         = 2 * pivot - support
    s1         = 2 * pivot - resistance
    return support, resistance, pivot, r1, s1

def detect_candlestick_patterns(df):
    patterns   = []
    o  = df["Open"].iloc[-1];  h = df["High"].iloc[-1]
    l  = df["Low"].iloc[-1];   c = df["Close"].iloc[-1]
    o2 = df["Open"].iloc[-2];  c2 = df["Close"].iloc[-2]
    body       = abs(c - o)
    full_range = h - l if h - l > 0 else 0.0001
    lower_wick = min(o, c) - l
    upper_wick = h - max(o, c)
    if body / full_range < 0.1:
        patterns.append(("DOJI", "neutral"))
    if lower_wick > 2 * body and upper_wick < body:
        patterns.append(("HAMMER", "call"))
    if upper_wick > 2 * body and lower_wick < body:
        patterns.append(("SHOOTING_STAR", "put"))
    if c2 < o2 and c > o and c > o2 and o < c2:
        patterns.append(("BULLISH_ENGULFING", "call"))
    if c2 > o2 and c < o and c < o2 and o > c2:
        patterns.append(("BEARISH_ENGULFING", "put"))
    if c > o and body / full_range > 0.7:
        patterns.append(("STRONG_BULL", "call"))
    if c < o and body / full_range > 0.7:
        patterns.append(("STRONG_BEAR", "put"))
    return patterns

def analyze_signal(df):
    close  = df["Close"]
    high   = df["High"]
    low    = df["Low"]
    volume = df["Volume"]

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
    df["BB_MID"] = bb[[c for c in bb_cols if c.startswith("BBM")][0]]
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

    def safe(val, default=0):
        return val if not pd.isna(val) else default

    r  = df.iloc[-1]
    r2 = df.iloc[-2]

    price    = r["Close"]
    rsi      = safe(r["RSI"],       50)
    rsi6     = safe(r["RSI_6"],     50)
    ema9     = safe(r["EMA_9"],     price)
    ema21    = safe(r["EMA_21"],    price)
    ema50    = safe(r["EMA_50"],    price)
    ema200   = safe(r["EMA_200"],   price)
    macd     = safe(r["MACD"],      0)
    macd_sig = safe(r["MACD_SIG"],  0)
    macd_h   = safe(r["MACD_HIST"], 0)
    macd_h2  = safe(r2["MACD_HIST"],0)
    bb_up    = safe(r["BB_UP"],     price * 1.01)
    bb_low_v = safe(r["BB_LOW"],    price * 0.99)
    bb_mid   = safe(r["BB_MID"],    price)
    stoch_k  = safe(r["STOCH_K"],   50)
    stoch_d  = safe(r["STOCH_D"],   50)
    stoch_k2 = safe(r2["STOCH_K"],  50)
    adx      = safe(r["ADX"],       0)
    di_pos   = safe(r["DI_POS"],    0)
    di_neg   = safe(r["DI_NEG"],    0)
    vol      = safe(r["Volume"],    0)
    vol_ma   = safe(r["VOL_MA"],    1)

    support, resistance, pivot, r1, s1 = get_support_resistance(df)
    patterns     = detect_candlestick_patterns(df)
    trend_strong = adx > 20
    trend_is_up  = trend_strong and di_pos > di_neg
    trend_is_down= trend_strong and di_neg > di_pos

    call_score   = 0
    put_score    = 0
    call_reasons = []
    put_reasons  = []

    # ── 1. RSI — Trend-Following Logic ────────────────────
    if rsi < 25:
        if not trend_is_down:
            call_score += 3
            call_reasons.append(f"RSI Strong Oversold ({rsi:.1f}) — reversal 🔥")
        else:
            put_score += 2
            put_reasons.append(f"RSI Oversold ({rsi:.1f}) laakiin Downtrend xooggan — trend-ride 📉")
    elif rsi < 35 and not trend_is_down:
        call_score += 2
        call_reasons.append(f"RSI Oversold ({rsi:.1f})")

    if rsi > 75:
        if not trend_is_up:
            put_score += 3
            put_reasons.append(f"RSI Strong Overbought ({rsi:.1f}) — reversal 🔥")
        else:
            call_score += 2
            call_reasons.append(f"RSI Overbought ({rsi:.1f}) laakiin Uptrend xooggan — trend-ride 📈")
    elif rsi > 65 and not trend_is_up:
        put_score += 2
        put_reasons.append(f"RSI Overbought ({rsi:.1f})")

    # Fast RSI
    if rsi6 < 20 and not trend_is_down:
        call_score += 1
        call_reasons.append(f"Fast RSI Oversold ({rsi6:.1f})")
    elif rsi6 > 80 and not trend_is_up:
        put_score += 1
        put_reasons.append(f"Fast RSI Overbought ({rsi6:.1f})")

    # ── 2. EMA — Trend Structure ─────────────────────────────────
    if ema9 > ema21 > ema50:
        call_score += 4
        call_reasons.append("EMA 9>21>50 — Strong Uptrend 🚀")
    elif ema9 > ema21:
        call_score += 1
        call_reasons.append("EMA 9 > EMA 21 (uptrend)")
    if ema9 < ema21 < ema50:
        put_score += 4
        put_reasons.append("EMA 9<21<50 — Strong Downtrend 📉")
    elif ema9 < ema21:
        put_score += 1
        put_reasons.append("EMA 9 < EMA 21 (downtrend)")

    if price > ema200:
        call_score += 1
        call_reasons.append("Price > EMA 200 (bull market macro)")
    else:
        put_score += 1
        put_reasons.append("Price < EMA 200 (bear market macro)")

    # ── 3. MACD ────────────────────────────────────────────────────────────
    if macd > macd_sig and macd_h > 0 and macd_h > macd_h2:
        call_score += 2
        call_reasons.append("MACD bullish + histogram koraya ✅")
    elif macd > macd_sig and macd_h > 0:
        call_score += 1
        call_reasons.append("MACD bullish zone")
    elif macd < macd_sig and macd_h < 0 and macd_h < macd_h2:
        put_score += 2
        put_reasons.append("MACD bearish + histogram hoos ✅")
    elif macd < macd_sig and macd_h < 0:
        put_score += 1
        put_reasons.append("MACD bearish zone")

    # ── 4. Bollinger Bands (FIXED: Removed noisy middle band triggers) ─────
    if price <= bb_low_v:
        if not trend_is_down:
            call_score += 3
            call_reasons.append("Price BB hoostiisa — bounce 🔥")
        else:
            put_score += 1
            put_reasons.append("Price BB hoostiisa laakiin downtrend — trend pressure ⚠️")
    elif price >= bb_up:
        if not trend_is_up:
            put_score += 3
            put_reasons.append("Price BB korkooda — reversal 🔥")
        else:
            call_score += 1
            call_reasons.append("Price BB korkooda laakiin uptrend — expansion ⚠️")

    # ── 5. Stochastic ───────────────────────────────────────────────────────
    if stoch_k < 20 and stoch_d < 20 and not trend_is_down:
        call_score += 2
        call_reasons.append(f"Stochastic Oversold ({stoch_k:.1f}) 🔥")
    elif stoch_k > stoch_d and stoch_k2 < stoch_d and stoch_k < 40:
        call_score += 2
        call_reasons.append("Stoch bullish cross ✅")
    if stoch_k > 80 and stoch_d > 80 and not trend_is_up:
        put_score += 2
        put_reasons.append(f"Stochastic Overbought ({stoch_k:.1f}) 🔥")
    elif stoch_k < stoch_d and stoch_k2 > stoch_d and stoch_k > 60:
        put_score += 2
        put_reasons.append("Stoch bearish cross ✅")

    # ── 6. ADX Momentum ─────────────────────────────────────────────────
    if trend_strong:
        if di_pos > di_neg:
            call_score += 3
            call_reasons.append(f"ADX xooggan ({adx:.1f}) — BUY momentum 🚀")
        else:
            put_score += 3
            put_reasons.append(f"ADX xooggan ({adx:.1f}) — SELL momentum 🚀")

    # ── 7. Support & Resistance ────────────────────────────────────────────
    sr_range = resistance - support
    if sr_range > 0:
        if abs(price - support) < sr_range * 0.05:
            call_score += 2
            call_reasons.append("Price Support dhow — bounce ✅")
        elif abs(price - resistance) < sr_range * 0.05:
            put_score += 2
            put_reasons.append("Price Resistance dhow — rejection ✅")

    # ── 8. Candlestick Patterns ────────────────────────────────────────────
    for pname, direction in patterns:
        if direction == "call":
            call_score += 2
            call_reasons.append(f"Pattern: {pname} 🕯️")
        elif direction == "put":
            put_score += 2
            put_reasons.append(f"Pattern: {pname} 🕯️")

    # ── 9. Volume Penalty Engine ──────────────────
    vol_confirm = (vol > vol_ma * 0.8) if vol_ma > 0 else False
    if vol_confirm:
        if call_score > put_score:
            call_score += 1
            call_reasons.append("Volume confirmed ✅")
        elif put_score > call_score:
            put_score += 1
            put_reasons.append("Volume confirmed ✅")
    else:
        call_score = max(0, call_score - 2)
        put_score  = max(0, put_score  - 2)
        penalty_msg = "⚠️ Volume daciif — 2 dhibcood baa laga gooyay (suuqu daciif yahay)"
        if call_score > put_score:
            call_reasons.append(penalty_msg)
        elif put_score > call_score:
            put_reasons.append(penalty_msg)
        else:
            call_reasons.append(penalty_msg)
            put_reasons.append(penalty_msg)

    # ── 10. Final Signal Engine ────────────
    total = (call_score + put_score) if (call_score + put_score) > 0 else 1

    if call_score > put_score and call_score >= 6:
        signal     = "CALL"
        confidence = min(50 + int((call_score / total) * 45), 95)
        reasons    = call_reasons
    elif put_score > call_score and put_score >= 6:
        signal     = "PUT"
        confidence = min(50 + int((put_score / total) * 45), 95)
        reasons    = put_reasons
    else:
        signal     = "WAIT"
        confidence = 0
        reasons    = ["Signal xooggan malahan — WAIT ✋"]
        if call_score > put_score:
            reasons.append(f"CALL dhinac ({call_score}) laakiin 6+ baahan")
        elif put_score > call_score:
            reasons.append(f"PUT dhinac ({put_score}) laakiin 6+ baahan")
        else:
            reasons.append(f"Indicators is burinayaan — CALL {call_score} vs PUT {put_score}")

    return {
        "signal": signal, "confidence": confidence,
        "reasons": reasons, "call_score": call_score, "put_score": put_score,
        "trend_strong": trend_strong, "trend_is_up": trend_is_up,
        "trend_is_down": trend_is_down, "adx": round(adx, 1),
        "patterns": patterns, "fetch_time": time.strftime("%H:%M:%S"),
        "indicators": {
            "Price":      round(price,      5),
            "RSI":        round(rsi,        2),
            "RSI_Fast":   round(rsi6,       2),
            "EMA_9":      round(ema9,       5),
            "EMA_21":     round(ema21,      5),
            "EMA_50":     round(ema50,      5),
            "MACD":       round(macd,       6),
            "MACD_Sig":   round(macd_sig,   6),
            "BB_Upper":   round(bb_up,      5),
            "BB_Lower":   round(bb_low_v,   5),
            "Stoch_K":    round(stoch_k,    2),
            "Stoch_D":    round(stoch_d,    2),
            "ADX":        round(adx,        2),
            "Support":    round(support,    5),
            "Resistance": round(resistance, 5),
        }
    }

# ── UI RENDERING ───────────────────────────────────────────────────────────
yahoo_ticker = get_yahoo_ticker(selected_pair)
st.caption(f"📡 Ticker: `{yahoo_ticker}` | Cache: 60s")

if st.button("⚡ GET LIVE SIGNAL", use_container_width=True):
    with st.spinner(f"Xog cusub la keenayaa {selected_pair}... ⏳"):
        try:
            df = fetch_market_data(yahoo_ticker, timeframe)

            if df.empty or len(df) < 50:
                st.error(f"Xog ku filan laga ma helin **{selected_pair}**.")
            else:
                result = analyze_signal(df)
                sig    = result["signal"]
                con    = result["confidence"]

                st.info(f"🕐 Xogta la keenay: **{result['fetch_time']}** | Candles: **{len(df)}** ✅")

                if sig == "CALL":
                    st.markdown(f"""
                    <div style='background:linear-gradient(135deg,#1a472a,#2d6a4f); padding:25px;border-radius:15px;text-align:center; border:3px solid #2ecc71;'>
                        <h1 style='color:#2ecc71;font-size:3.5em;margin:0'>🟩 CALL ↑</h1>
                        <h2 style='color:white;margin:8px 0'>Kalsooni: {con}%</h2>
                    </div>""", unsafe_allow_html=True)
                elif sig == "PUT":
                    st.markdown(f"""
                    <div style='background:linear-gradient(135deg,#4a1122,#6b2737); padding:25px;border-radius:15px;text-align:center; border:3px solid #e74c3c;'>
                        <h1 style='color:#e74c3c;font-size:3.5em;margin:0'>🟥 PUT ↓</h1>
                        <h2 style='color:white;margin:8px 0'>Kalsooni: {con}%</h2>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='background:linear-gradient(135deg,#3d3200,#5c4a00); padding:25px;border-radius:15px;text-align:center; border:3px solid #f39c12;'>
                        <h1 style='color:#f39c12;font-size:3.5em;margin:0'>🟨 WAIT ✋</h1>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                if result["trend_strong"]:
                    direction = "KORE (CALL)" if result["trend_is_up"] else "HOOSE (PUT)"
                    st.info(f"📈 Trend XOOGGAN (ADX: {result['adx']}) — Jihada: {direction}")
                else:
                    st.warning(f"⚠️ Trend DACIIF (ADX: {result['adx']}) — Market sideways, taxaddar")

                st.subheader("📋 Sababaha Signal-ka:")
                for reason in result["reasons"]:
                    st.write(f"• {reason}")

                with st.expander("📊 Dhammaan Indicators-ka"):
                    ind = result["indicators"]
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Price", ind["Price"]); st.metric("RSI", ind["RSI"])
                    with c2:
                        st.metric("EMA 9", ind["EMA_9"]); st.metric("MACD", ind["MACD"])
                    with c3:
                        st.metric("ADX", ind["ADX"]); st.metric("Support", ind["Support"])
        except Exception as e:
            st.error(f"Cilad: {str(e)}")
