import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import time

st.set_page_config(
    page_title="Mahad AI - Live Signal Bot v3",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ PROV MAHAD ULTIMATE AI v3")
st.write("High Accuracy Scanner | Multi-Indicator + Pattern + Trend Confirmation")

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

col1, col2 = st.columns(2)
with col1:
    selected_pair = st.selectbox("Dooro Pair-ka:", POCKET_OPTION_PAIRS)
with col2:
    timeframe = st.selectbox("Timeframe:", ["1m", "2m", "3m", "5m"])


def get_yahoo_ticker(pair_name):
    clean_pair = pair_name.replace(" OTC", "")
    mapping = {
        "AUD/USD": "AUDUSD=X", "EUR/USD": "EURUSD=X", "EUR/JPY": "EURJPY=X",
        "AUD/JPY": "AUDJPY=X", "USD/JPY": "JPY=X",   "EUR/CAD": "EURCAD=X",
        "USD/CAD": "CAD=X",    "USD/CHF": "CHF=X",    "EUR/CHF": "EURCHF=X",
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


# ── CACHE LA'AAAN — xog cusub mar walba ─────────
def fetch_market_data(ticker_name, tf):
    fetch_tf = "1m" if tf in ["2m", "3m"] else tf
    ticker = yf.Ticker(ticker_name)
    # Period 5d si xog badan loo helo
    df = ticker.history(period="5d", interval=fetch_tf)
    if df.empty:
        return df
    if tf == "2m":
        df = df.resample('2min').agg({
            'Open':'first','High':'max',
            'Low':'min','Close':'last','Volume':'sum'
        })
    elif tf == "3m":
        df = df.resample('3min').agg({
            'Open':'first','High':'max',
            'Low':'min','Close':'last','Volume':'sum'
        })
    return df.dropna()


def get_support_resistance(df, lookback=50):
    recent     = df.tail(lookback)
    resistance = recent['High'].max()
    support    = recent['Low'].min()
    pivot      = (resistance + support + recent['Close'].iloc[-1]) / 3
    r1         = 2 * pivot - support
    s1         = 2 * pivot - resistance
    return support, resistance, pivot, r1, s1


def detect_candlestick_patterns(df):
    patterns  = []
    o  = df['Open'].iloc[-1];  h = df['High'].iloc[-1]
    l  = df['Low'].iloc[-1];   c = df['Close'].iloc[-1]
    o2 = df['Open'].iloc[-2];  c2= df['Close'].iloc[-2]
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
    close  = df['Close']
    high   = df['High']
    low    = df['Low']
    volume = df['Volume']

    df['RSI']     = ta.rsi(close, length=14)
    df['RSI_6']   = ta.rsi(close, length=6)
    df['EMA_9']   = ta.ema(close, length=9)
    df['EMA_21']  = ta.ema(close, length=21)
    df['EMA_50']  = ta.ema(close, length=50)
    df['EMA_200'] = ta.ema(close, length=200)

    macd_df      = ta.macd(close, fast=12, slow=26, signal=9)
    macd_cols    = macd_df.columns.tolist()
    df['MACD']      = macd_df[macd_cols[0]]
    df['MACD_SIG']  = macd_df[macd_cols[1]]
    df['MACD_HIST'] = macd_df[macd_cols[2]]

    bb      = ta.bbands(close, length=20, std=2)
    bb_cols = bb.columns.tolist()
    df['BB_LOW'] = bb[[c for c in bb_cols if c.startswith('BBL')][0]]
    df['BB_MID'] = bb[[c for c in bb_cols if c.startswith('BBM')][0]]
    df['BB_UP']  = bb[[c for c in bb_cols if c.startswith('BBU')][0]]

    stoch      = ta.stoch(high, low, close, k=14, d=3)
    stoch_cols = stoch.columns.tolist()
    df['STOCH_K'] = stoch[stoch_cols[0]]
    df['STOCH_D'] = stoch[stoch_cols[1]]

    adx_df   = ta.adx(high, low, close, length=14)
    adx_cols = adx_df.columns.tolist()
    df['ADX']    = adx_df[[c for c in adx_cols if c.startswith('ADX_')][0]]
    df['DI_POS'] = adx_df[[c for c in adx_cols if 'DMP' in c][0]]
    df['DI_NEG'] = adx_df[[c for c in adx_cols if 'DMN' in c][0]]

    df['ATR']    = ta.atr(high, low, close, length=14)
    df['VOL_MA'] = volume.rolling(20).mean()

    def safe(val, default=0):
        return val if not pd.isna(val) else default

    r  = df.iloc[-1]
    r2 = df.iloc[-2]

    price    = r['Close']
    rsi      = safe(r['RSI'],       50)
    rsi6     = safe(r['RSI_6'],     50)
    ema9     = safe(r['EMA_9'],     price)
    ema21    = safe(r['EMA_21'],    price)
    ema50    = safe(r['EMA_50'],    price)
    ema200   = safe(r['EMA_200'],   price)
    macd     = safe(r['MACD'],      0)
    macd_sig = safe(r['MACD_SIG'],  0)
    macd_h   = safe(r['MACD_HIST'], 0)
    macd_h2  = safe(r2['MACD_HIST'],0)
    bb_up    = safe(r['BB_UP'],     price * 1.01)
    bb_low   = safe(r['BB_LOW'],    price * 0.99)
    bb_mid   = safe(r['BB_MID'],    price)
    stoch_k  = safe(r['STOCH_K'],   50)
    stoch_d  = safe(r['STOCH_D'],   50)
    stoch_k2 = safe(r2['STOCH_K'],  50)
    adx      = safe(r['ADX'],       0)
    di_pos   = safe(r['DI_POS'],    0)
    di_neg   = safe(r['DI_NEG'],    0)
    vol      = safe(r['Volume'],    0)
    vol_ma   = safe(r['VOL_MA'],    1)

    support, resistance, pivot, r1, s1 = get_support_resistance(df)
    patterns   = detect_candlestick_patterns(df)
    trend_strong = adx > 20

    call_score   = 0
    put_score    = 0
    call_reasons = []
    put_reasons  = []

    # RSI
    if rsi < 25:
        call_score += 3; call_reasons.append(f"RSI aad u hooseeya ({rsi:.1f}) — strong oversold 🔥")
    elif rsi < 35:
        call_score += 2; call_reasons.append(f"RSI oversold ({rsi:.1f})")
    elif rsi > 75:
        put_score += 3;  put_reasons.append(f"RSI aad u sarreeya ({rsi:.1f}) — strong overbought 🔥")
    elif rsi > 65:
        put_score += 2;  put_reasons.append(f"RSI overbought ({rsi:.1f})")

    # Fast RSI
    if rsi6 < 20:
        call_score += 1; call_reasons.append(f"Fast RSI oversold ({rsi6:.1f})")
    elif rsi6 > 80:
        put_score += 1;  put_reasons.append(f"Fast RSI overbought ({rsi6:.1f})")

    # EMA
    if ema9 > ema21 > ema50:
        call_score += 3; call_reasons.append("EMA 9>21>50 — Strong uptrend 🔥")
    elif ema9 > ema21:
        call_score += 1; call_reasons.append("EMA 9 > EMA 21 (uptrend)")
    elif ema9 < ema21 < ema50:
        put_score += 3;  put_reasons.append("EMA 9<21<50 — Strong downtrend 🔥")
    elif ema9 < ema21:
        put_score += 1;  put_reasons.append("EMA 9 < EMA 21 (downtrend)")

    if price > ema200:
        call_score += 1; call_reasons.append("Price > EMA 200 (bull market)")
    else:
        put_score += 1;  put_reasons.append("Price < EMA 200 (bear market)")

    # MACD
    if macd > macd_sig and macd_h > 0 and macd_h > macd_h2:
        call_score += 2; call_reasons.append("MACD bullish + histogram koraya ✅")
    elif macd > macd_sig and macd_h > 0:
        call_score += 1; call_reasons.append("MACD bullish")
    elif macd < macd_sig and macd_h < 0 and macd_h < macd_h2:
        put_score += 2;  put_reasons.append("MACD bearish + histogram hoos ✅")
    elif macd < macd_sig and macd_h < 0:
        put_score += 1;  put_reasons.append("MACD bearish")

    # Bollinger Bands
    bb_width = (bb_up - bb_low) / bb_mid if bb_mid > 0 else 0
    if price <= bb_low:
        call_score += 3; call_reasons.append("Price BB hoostiisa — bounce 🔥")
    elif price >= bb_up:
        put_score += 3;  put_reasons.append("Price BB korkooda — reversal 🔥")
    elif price < bb_mid and bb_width > 0.001:
        call_score += 1; call_reasons.append("Price BB dhexda hoostiisa")
    elif price > bb_mid and bb_width > 0.001:
        put_score += 1;  put_reasons.append("Price BB dhexda korkooda")

    # Stochastic
    if stoch_k < 20 and stoch_d < 20:
        call_score += 3; call_reasons.append(f"Stochastic oversold ({stoch_k:.1f}) 🔥")
    elif stoch_k > stoch_d and stoch_k2 < stoch_d and stoch_k < 40:
        call_score += 2; call_reasons.append("Stoch bullish cross ✅")
    elif stoch_k > 80 and stoch_d > 80:
        put_score += 3;  put_reasons.append(f"Stochastic overbought ({stoch_k:.1f}) 🔥")
    elif stoch_k < stoch_d and stoch_k2 > stoch_d and stoch_k > 60:
        put_score += 2;  put_reasons.append("Stoch bearish cross ✅")

    # ADX
    if trend_strong:
        if di_pos > di_neg:
            call_score += 2; call_reasons.append(f"ADX xooggan ({adx:.1f}) — CALL direction 🔥")
        else:
            put_score += 2;  put_reasons.append(f"ADX xooggan ({adx:.1f}) — PUT direction 🔥")

    # Support & Resistance
    sr_range = resistance - support
    if sr_range > 0:
        if abs(price - support) < sr_range * 0.05:
            call_score += 2; call_reasons.append("Price Support dhow — bounce ✅")
        elif abs(price - resistance) < sr_range * 0.05:
            put_score += 2;  put_reasons.append("Price Resistance dhow — rejection ✅")

    # Candlestick
    for pname, direction in patterns:
        if direction == "call":
            call_score += 2; call_reasons.append(f"Pattern: {pname} 🕯️")
        elif direction == "put":
            put_score += 2;  put_reasons.append(f"Pattern: {pname} 🕯️")

    # Volume
    vol_confirm = vol > vol_ma * 0.8 if vol_ma > 0 else True
    if vol_confirm:
        if call_score >= put_score:
            call_score += 1; call_reasons.append("Volume confirmed ✅")
        else:
            put_score += 1;  put_reasons.append("Volume confirmed ✅")

    total = (call_score + put_score) if (call_score + put_score) > 0 else 1

    if call_score > put_score and call_score >= 8:
        signal     = "CALL"
        confidence = min(50 + int((call_score / total) * 45), 82)
        reasons    = call_reasons
    elif put_score > call_score and put_score >= 8:
        signal     = "PUT"
        confidence = min(50 + int((put_score / total) * 45), 82)
        reasons    = put_reasons
    else:
        signal     = "WAIT"
        confidence = 0
        reasons    = ["Signal xooggan malahan — WAIT ✋"]
        if call_score > put_score:
            reasons.append(f"CALL dhinac u jeedaa laakiin score ({call_score}) waa yar (8 baahan)")
        elif put_score > call_score:
            reasons.append(f"PUT dhinac u jeedaa laakiin score ({put_score}) waa yar (8 baahan)")

    return {
        "signal": signal, "confidence": confidence,
        "reasons": reasons, "call_score": call_score,
        "put_score": put_score, "trend_strong": trend_strong,
        "adx": round(adx, 1), "patterns": patterns,
        "fetch_time": time.strftime("%H:%M:%S"),
        "indicators": {
            "Price": round(price, 5), "RSI": round(rsi, 2),
            "RSI_Fast": round(rsi6, 2), "EMA_9": round(ema9, 5),
            "EMA_21": round(ema21, 5),  "EMA_50": round(ema50, 5),
            "MACD": round(macd, 6),     "MACD_Sig": round(macd_sig, 6),
            "BB_Upper": round(bb_up, 5),"BB_Lower": round(bb_low, 5),
            "Stoch_K": round(stoch_k, 2),"Stoch_D": round(stoch_d, 2),
            "ADX": round(adx, 2),       "Support": round(support, 5),
            "Resistance": round(resistance, 5),
        }
    }


yahoo_ticker = get_yahoo_ticker(selected_pair)

if st.button("⚡ GET LIVE SIGNAL", use_container_width=True):
    with st.spinner(f"Xog cusub la keenayaa {selected_pair}... ⏳"):
        try:
            # Cache clear si xog cusub loo helo
            st.cache_data.clear()

            df = fetch_market_data(yahoo_ticker, timeframe)

            if df.empty or len(df) < 200:
                st.error(f"Xog ku filan laga ma helin {selected_pair}. Isku day mar kale.")
            else:
                result   = analyze_signal(df)
                sig      = result['signal']
                con      = result['confidence']

                # Waqtiga xogta la keenay
                st.info(f"🕐 Xogta waxaa la keenay: {result['fetch_time']} — Xog cusub ✅")

                if sig == "CALL":
                    st.markdown(f"""
                    <div style='background:linear-gradient(135deg,#1a472a,#2d6a4f);
                                padding:25px;border-radius:15px;text-align:center;
                                border:3px solid #2ecc71;box-shadow:0 0 20px #2ecc7166;'>
                        <h1 style='color:#2ecc71;font-size:3.5em;margin:0'>🟩 CALL ↑</h1>
                        <h2 style='color:white;margin:8px 0'>Kalsooni: {con}%</h2>
                        <div style='background:#ffffff22;border-radius:8px;padding:8px;margin-top:10px;'>
                            <span style='color:#aaffaa;font-size:1.1em'>
                                CALL {result['call_score']} vs PUT {result['put_score']}
                            </span>
                        </div>
                    </div>""", unsafe_allow_html=True)

                elif sig == "PUT":
                    st.markdown(f"""
                    <div style='background:linear-gradient(135deg,#4a1122,#6b2737);
                                padding:25px;border-radius:15px;text-align:center;
                                border:3px solid #e74c3c;box-shadow:0 0 20px #e74c3c66;'>
                        <h1 style='color:#e74c3c;font-size:3.5em;margin:0'>🟥 PUT ↓</h1>
                        <h2 style='color:white;margin:8px 0'>Kalsooni: {con}%</h2>
                        <div style='background:#ffffff22;border-radius:8px;padding:8px;margin-top:10px;'>
                            <span style='color:#ffaaaa;font-size:1.1em'>
                                PUT {result['put_score']} vs CALL {result['call_score']}
                            </span>
                        </div>
                    </div>""", unsafe_allow_html=True)

                else:
                    st.markdown(f"""
                    <div style='background:linear-gradient(135deg,#3d3200,#5c4a00);
                                padding:25px;border-radius:15px;text-align:center;
                                border:3px solid #f39c12;'>
                        <h1 style='color:#f39c12;font-size:3.5em;margin:0'>🟨 WAIT ✋</h1>
                        <h2 style='color:#aaa;margin:8px 0'>Signal xooggan malahan</h2>
                        <div style='background:#ffffff22;border-radius:8px;padding:8px;margin-top:10px;'>
                            <span style='color:#ffddaa;font-size:1.1em'>
                                CALL {result['call_score']} vs PUT {result['put_score']} — 8+ baahan
                            </span>
                        </div>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                if result['trend_strong']:
                    st.info(f"📈 Trend XOOGGAN (ADX: {result['adx']}) — Signal믿elo karo")
                else:
                    st.warning(f"⚠️ Trend DACIIF (ADX: {result['adx']}) — Market sideways, taxaddar")

                if result['patterns']:
                    pats = ", ".join([p[0] for p in result['patterns']])
                    st.success(f"🕯️ Candlestick: {pats}")

                st.subheader("📋 Sababaha Signal-ka:")
                for reason in result['reasons']:
                    st.write(f"• {reason}")

                with st.expander("📊 Dhammaan Indicators-ka"):
                    ind = result['indicators']
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Price",    ind['Price'])
                        st.metric("RSI",      ind['RSI'])
                        st.metric("RSI Fast", ind['RSI_Fast'])
                        st.metric("Stoch K",  ind['Stoch_K'])
                        st.metric("Stoch D",  ind['Stoch_D'])
                    with c2:
                        st.metric("EMA 9",    ind['EMA_9'])
                        st.metric("EMA 21",   ind['EMA_21'])
                        st.metric("EMA 50",   ind['EMA_50'])
                        st.metric("MACD",     ind['MACD'])
                        st.metric("MACD Sig", ind['MACD_Sig'])
                    with c3:
                        st.metric("ADX",        ind['ADX'])
                        st.metric("BB Upper",   ind['BB_Upper'])
                        st.metric("BB Lower",   ind['BB_Lower'])
                        st.metric("Support",    ind['Support'])
                        st.metric("Resistance", ind['Resistance'])

        except Exception as e:
            st.error(f"Cilad: {str(e)}")
            st.error(f"Nooca ciladda: {type(e).__name__}")

st.markdown("---")
st.caption("⚠️ Trading-ku khatarna waa. Signal-kani waa taageero keliya — demo ku tijaabi marka hore.")
