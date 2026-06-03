import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

st.set_page_config(
    page_title="Mahad AI - Live Signal Bot",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ PROV MAHAD ULTIMATE AI v2")
st.write("Live Market Scanner - API Key La'aaan | Yahoo Finance + Multi-Indicator Analysis")

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


@st.cache_data(ttl=30, show_spinner=False)
def fetch_market_data(ticker_name, tf):
    fetch_tf = "1m" if tf in ["2m", "3m"] else tf
    ticker = yf.Ticker(ticker_name)
    df = ticker.history(period="2d", interval=fetch_tf)
    if df.empty:
        return df
    if tf == "2m":
        df = df.resample('2min').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'})
    elif tf == "3m":
        df = df.resample('3min').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'})
    return df.dropna()


def analyze_signal(df):
    close = df['Close']
    high  = df['High']
    low   = df['Low']

    # ── Indicators ──────────────────────────────
    df['RSI']    = ta.rsi(close, length=14)
    df['EMA_9']  = ta.ema(close, length=9)
    df['EMA_21'] = ta.ema(close, length=21)
    df['EMA_50'] = ta.ema(close, length=50)

    # MACD
    macd_df = ta.macd(close, fast=12, slow=26, signal=9)
    macd_cols = macd_df.columns.tolist()
    df['MACD']      = macd_df[macd_cols[0]]  # MACD line
    df['MACD_SIG']  = macd_df[macd_cols[1]]  # Signal line
    df['MACD_HIST'] = macd_df[macd_cols[2]]  # Histogram

    # Bollinger Bands - column name ku hel si toos ah
    bb = ta.bbands(close, length=20, std=2)
    bb_cols = bb.columns.tolist()
    # Columns: Lower, Mid, Upper, Bandwidth, Percent
    bb_lower_col = [c for c in bb_cols if c.startswith('BBL')][0]
    bb_mid_col   = [c for c in bb_cols if c.startswith('BBM')][0]
    bb_upper_col = [c for c in bb_cols if c.startswith('BBU')][0]
    df['BB_LOW'] = bb[bb_lower_col]
    df['BB_MID'] = bb[bb_mid_col]
    df['BB_UP']  = bb[bb_upper_col]

    # Stochastic
    stoch = ta.stoch(high, low, close, k=14, d=3)
    stoch_cols = stoch.columns.tolist()
    df['STOCH_K'] = stoch[stoch_cols[0]]
    df['STOCH_D'] = stoch[stoch_cols[1]]

    df['ATR'] = ta.atr(high, low, close, length=14)

    # ── Qiimayaasha ugu dambeeyay ────────────────
    r  = df.iloc[-1]
    r2 = df.iloc[-2]

    rsi      = r['RSI']      if not pd.isna(r['RSI'])      else 50
    ema9     = r['EMA_9']    if not pd.isna(r['EMA_9'])    else 0
    ema21    = r['EMA_21']   if not pd.isna(r['EMA_21'])   else 0
    ema50    = r['EMA_50']   if not pd.isna(r['EMA_50'])   else 0
    macd     = r['MACD']     if not pd.isna(r['MACD'])     else 0
    macd_sig = r['MACD_SIG'] if not pd.isna(r['MACD_SIG']) else 0
    macd_h   = r['MACD_HIST']if not pd.isna(r['MACD_HIST'])else 0
    bb_up    = r['BB_UP']    if not pd.isna(r['BB_UP'])    else 0
    bb_low   = r['BB_LOW']   if not pd.isna(r['BB_LOW'])   else 0
    bb_mid   = r['BB_MID']   if not pd.isna(r['BB_MID'])   else 0
    stoch_k  = r['STOCH_K']  if not pd.isna(r['STOCH_K'])  else 50
    stoch_d  = r['STOCH_D']  if not pd.isna(r['STOCH_D'])  else 50
    price    = r['Close']
    atr      = r['ATR']      if not pd.isna(r['ATR'])      else 0
    prev_macd_h = r2['MACD_HIST'] if not pd.isna(r2['MACD_HIST']) else 0

    # ── Xisaabinta dhibcaha ────────────────────
    call_score = 0
    put_score  = 0
    call_reasons = []
    put_reasons  = []

    # RSI
    if rsi < 30:
        call_score += 3
        call_reasons.append(f"RSI aad u hooseeya ({rsi:.1f}) — oversold 🔥")
    elif rsi < 40:
        call_score += 2
        call_reasons.append(f"RSI hooseeya ({rsi:.1f})")
    elif rsi > 70:
        put_score += 3
        put_reasons.append(f"RSI aad u sarreeya ({rsi:.1f}) — overbought 🔥")
    elif rsi > 60:
        put_score += 2
        put_reasons.append(f"RSI sarreeya ({rsi:.1f})")

    # EMA Cross
    if ema9 > ema21:
        call_score += 2
        call_reasons.append("EMA 9 > EMA 21 (uptrend)")
    else:
        put_score += 2
        put_reasons.append("EMA 9 < EMA 21 (downtrend)")

    if price > ema50:
        call_score += 1
        call_reasons.append("Qiimahu ka sareeya EMA 50")
    else:
        put_score += 1
        put_reasons.append("Qiimahu ka hooseeya EMA 50")

    # MACD
    if macd > macd_sig and macd_h > 0:
        call_score += 2
        call_reasons.append("MACD positive crossover ✅")
    elif macd < macd_sig and macd_h < 0:
        put_score += 2
        put_reasons.append("MACD negative crossover ✅")

    if macd_h > prev_macd_h and macd_h > 0:
        call_score += 1
        call_reasons.append("MACD histogram kor u socda")
    elif macd_h < prev_macd_h and macd_h < 0:
        put_score += 1
        put_reasons.append("MACD histogram hoos u socda")

    # Bollinger Bands
    if bb_up > 0 and bb_low > 0:
        if price <= bb_low:
            call_score += 3
            call_reasons.append("Qiimahu BB hoostiisa — bounce la filayo 🔥")
        elif price >= bb_up:
            put_score += 3
            put_reasons.append("Qiimahu BB korkooda — hoos u dhac la filayo 🔥")
        elif price < bb_mid:
            call_score += 1
            call_reasons.append("Qiimahu BB dhexda hoostiisa")
        else:
            put_score += 1
            put_reasons.append("Qiimahu BB dhexda korkooda")

    # Stochastic
    if stoch_k < 20 and stoch_d < 20:
        call_score += 3
        call_reasons.append(f"Stochastic oversold ({stoch_k:.1f}) 🔥")
    elif stoch_k < 30:
        call_score += 1
        call_reasons.append(f"Stochastic hooseeya ({stoch_k:.1f})")
    elif stoch_k > 80 and stoch_d > 80:
        put_score += 3
        put_reasons.append(f"Stochastic overbought ({stoch_k:.1f}) 🔥")
    elif stoch_k > 70:
        put_score += 1
        put_reasons.append(f"Stochastic sarreeya ({stoch_k:.1f})")

    if stoch_k > stoch_d and stoch_k < 50:
        call_score += 1
        call_reasons.append("Stoch bullish cross")
    elif stoch_k < stoch_d and stoch_k > 50:
        put_score += 1
        put_reasons.append("Stoch bearish cross")

    # ── Go'aanka ──────────────────────────────
    total = call_score + put_score if (call_score + put_score) > 0 else 1

    if call_score > put_score and call_score >= 6:
        signal     = "CALL"
        confidence = min(int((call_score / total) * 100), 95)
        reasons    = call_reasons
    elif put_score > call_score and put_score >= 6:
        signal     = "PUT"
        confidence = min(int((put_score / total) * 100), 95)
        reasons    = put_reasons
    else:
        signal     = "WAIT"
        confidence = 50
        reasons    = ["Xog aad u cad malahan — suug signal xooggan"]

    return {
        "signal": signal,
        "confidence": confidence,
        "reasons": reasons,
        "call_score": call_score,
        "put_score": put_score,
        "indicators": {
            "RSI": round(rsi, 2),
            "EMA_9": round(ema9, 5),
            "EMA_21": round(ema21, 5),
            "EMA_50": round(ema50, 5),
            "MACD": round(macd, 5),
            "MACD_Signal": round(macd_sig, 5),
            "BB_Upper": round(bb_up, 5),
            "BB_Lower": round(bb_low, 5),
            "Stoch_K": round(stoch_k, 2),
            "Stoch_D": round(stoch_d, 2),
            "Price": round(price, 5),
        }
    }


yahoo_ticker = get_yahoo_ticker(selected_pair)

if st.button("⚡ GET LIVE SIGNAL", use_container_width=True):
    with st.spinner(f"Xog la keenayaa {selected_pair}..."):
        try:
            df = fetch_market_data(yahoo_ticker, timeframe)

            if df.empty or len(df) < 55:
                st.error(f"Xog ku filan laga ma helin {selected_pair}. Isku day mar kale.")
            else:
                result = analyze_signal(df)
                sig = result['signal']
                con = result['confidence']

                st.success(f"✅ Signal diyaar — {selected_pair} ({timeframe})")

                if sig == "CALL":
                    st.markdown(f"""
                    <div style='background:#1a472a;padding:20px;border-radius:12px;
                                text-align:center;border:2px solid #2ecc71;'>
                        <h1 style='color:#2ecc71;font-size:3em;margin:0'>🟩 CALL ↑</h1>
                        <h2 style='color:white;margin:5px 0'>Kalsooni: {con}%</h2>
                        <p style='color:#aaa;margin:0'>
                            Dhibcaha: CALL {result['call_score']} vs PUT {result['put_score']}
                        </p>
                    </div>""", unsafe_allow_html=True)
                elif sig == "PUT":
                    st.markdown(f"""
                    <div style='background:#4a1122;padding:20px;border-radius:12px;
                                text-align:center;border:2px solid #e74c3c;'>
                        <h1 style='color:#e74c3c;font-size:3em;margin:0'>🟥 PUT ↓</h1>
                        <h2 style='color:white;margin:5px 0'>Kalsooni: {con}%</h2>
                        <p style='color:#aaa;margin:0'>
                            Dhibcaha: CALL {result['call_score']} vs PUT {result['put_score']}
                        </p>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='background:#3d3200;padding:20px;border-radius:12px;
                                text-align:center;border:2px solid #f39c12;'>
                        <h1 style='color:#f39c12;font-size:3em;margin:0'>🟨 WAIT</h1>
                        <h2 style='color:white;margin:5px 0'>Kalsooni: {con}%</h2>
                        <p style='color:#aaa;margin:0'>
                            Dhibcaha: CALL {result['call_score']} vs PUT {result['put_score']}
                        </p>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                st.subheader("📋 Sababaha Signal-ka:")
                for reason in result['reasons']:
                    st.write(f"• {reason}")

                with st.expander("📊 Dhammaan Indicators-ka"):
                    ind = result['indicators']
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("RSI",     ind['RSI'])
                        st.metric("Stoch K", ind['Stoch_K'])
                        st.metric("Stoch D", ind['Stoch_D'])
                    with c2:
                        st.metric("EMA 9",  ind['EMA_9'])
                        st.metric("EMA 21", ind['EMA_21'])
                        st.metric("EMA 50", ind['EMA_50'])
                    with c3:
                        st.metric("MACD",     ind['MACD'])
                        st.metric("BB Upper", ind['BB_Upper'])
                        st.metric("BB Lower", ind['BB_Lower'])

        except Exception as e:
            st.error(f"Cilad: {str(e)}")

st.markdown("---")
st.caption("⚠️ Trading-ku khatarna waa. Signal-kani waa taageero keliya, maaha la-taliye maaliyadeed.")
