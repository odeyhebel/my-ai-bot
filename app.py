import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import json
import urllib.request
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="PROV MAHAD - 3-AI Ensemble Elite", layout="wide", initial_sidebar_state="collapsed")

# ──────────────────────────────────────────────────────────────
# 1) NEWS TRACKER (LIVE FOREX FACTORY)
# ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_news_calendar():
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
        df = pd.DataFrame(data)
        if not df.empty:
            df['datetime'] = pd.to_datetime(df['date'], utc=True)
        return df
    except Exception:
        return pd.DataFrame()

def check_pair_news(news_df, pair_name):
    if news_df.empty:
        return [], False

    currencies = pair_name.split("/")
    now = pd.Timestamp.now(tz='UTC')

    relevant = news_df[
        (news_df['country'].isin(currencies)) & 
        (news_df['impact'].isin(['High', 'Medium']))
    ].copy()

    if relevant.empty:
        return [], False

    high_risk = False
    upcoming_events = []

    for _, row in relevant.iterrows():
        if pd.isna(row['datetime']):
            continue
            
        event_time = pd.to_datetime(row['datetime'], utc=True)
        diff_minutes = (event_time - now).total_seconds() / 60.0

        if -30 <= diff_minutes <= 60:
            if row['impact'] == 'High':
                high_risk = True
            upcoming_events.append({
                'title': row['title'],
                'country': row['country'],
                'impact': row['impact'],
                'time': event_time.strftime('%H:%M UTC'),
                'diff': int(diff_minutes)
            })

    return upcoming_events, high_risk

# ──────────────────────────────────────────────────────────────
# 2) ADVANCED TECHNICAL INDICATORS & PRICE ACTION
# ──────────────────────────────────────────────────────────────

def calc_rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)

def calc_macd(close, fast=12, slow=26, signal=9):
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def calc_bollinger(close, period=20, std_mult=2):
    sma = close.rolling(period).mean()
    std = close.rolling(period).std()
    upper = sma + std_mult * std
    lower = sma - std_mult * std
    percent_b = (close - lower) / (upper - lower).replace(0, np.nan)
    return percent_b.fillna(0.5)

def calc_stochastic(high, low, close, period=14):
    lowest = low.rolling(period).min()
    highest = high.rolling(period).max()
    k = (close - lowest) / (highest - lowest).replace(0, np.nan) * 100
    return k.fillna(50)

def calc_adx(high, low, close, period=14):
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    plus_dm[(plus_dm - minus_dm) < 0] = 0
    minus_dm[(minus_dm - plus_dm) < 0] = 0

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    plus_di = 100 * (plus_dm.ewm(alpha=1/period, min_periods=period, adjust=False).mean() / atr.replace(0, np.nan))
    minus_di = 100 * (minus_dm.ewm(alpha=1/period, min_periods=period, adjust=False).mean() / atr.replace(0, np.nan))
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    adx = dx.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    return adx.fillna(0), plus_di.fillna(0), minus_di.fillna(0)

# ──────────────────────────────────────────────────────────────
# 3) DATA DOWNLOAD & MACRO MTF CHECKER
# ──────────────────────────────────────────────────────────────

PAIRS = {
    "EUR/USD": "EURUSD=X",
    "EUR/JPY": "EURJPY=X",
    "EUR/CHF": "EURCHF=X",
    "EUR/CAD": "EURCAD=X",
    "EUR/AUD": "EURAUD=X",
    "AUD/USD": "AUDUSD=X",
    "AUD/JPY": "AUDJPY=X",
    "AUD/CHF": "AUDCHF=X",
    "AUD/CAD": "AUDCAD=X",
    "CAD/CHF": "CADCHF=X",
    "CAD/JPY": "CADJPY=X",
    "CHF/JPY": "CHFJPY=X",
    "USD/CAD": "USDCAD=X",
    "USD/CHF": "USDCHF=X",
    "USD/JPY": "USDJPY=X",
    "GBP/USD": "GBPUSD=X",
    "GBP/AUD": "GBPAUD=X"
}

INTERVAL_PERIOD_MAP = {
    "1m":  "7d",
    "3m":  "7d",
    "5m":  "60d",
    "15m": "60d",
    "1h":  "730d",
}

RESAMPLE_INTERVALS = {
    "3m": ("1m", "3min"),
}

def _download_raw(ticker, interval, period):
    import yfinance as yf
    df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.dropna()

def _resample_ohlc(df, rule):
    agg = {"Open": "first", "High": "max", "Low": "min", "Close": "last"}
    if "Volume" in df.columns:
        agg["Volume"] = "sum"
    out = df.resample(rule).agg(agg)
    return out.dropna()

@st.cache_data(ttl=30, show_spinner=False)
def fetch_data(ticker, interval):
    if interval in RESAMPLE_INTERVALS:
        base_interval, rule = RESAMPLE_INTERVALS[interval]
        base_period = INTERVAL_PERIOD_MAP.get(base_interval, "7d")
        raw = _download_raw(ticker, base_interval, base_period)
        df = _resample_ohlc(raw, rule)
    else:
        period = INTERVAL_PERIOD_MAP.get(interval, "60d")
        df = _download_raw(ticker, interval, period)
        
    if len(df) > 2:
        df = df.iloc[:-1]
    return df

def get_macro_trend(ticker):
    try:
        df_macro = _download_raw(ticker, "1h", "30d")
        if len(df_macro) > 50:
            ema50 = df_macro["Close"].ewm(span=50, adjust=False).mean().iloc[-1]
            current_close = df_macro["Close"].iloc[-1]
            return "BULLISH (Kor)" if current_close > ema50 else "BEARISH (Hoos)"
    except Exception:
        pass
    return "NEUTRAL"

# ──────────────────────────────────────────────────────────────
# 4) ELITE FEATURE & LABEL ENGINEERING
# ──────────────────────────────────────────────────────────────

def build_features(df):
    out = pd.DataFrame(index=df.index)
    close, high, low, open_p = df["Close"], df["High"], df["Low"], df["Open"]

    out["rsi"] = calc_rsi(close, 14)
    _, _, macd_hist = calc_macd(close)
    out["macd_hist"] = macd_hist
    out["bb_percent"] = calc_bollinger(close, 20, 2)
    out["stoch_k"] = calc_stochastic(high, low, close, 14)
    adx, plus_di, minus_di = calc_adx(high, low, close, 14)
    out["adx"] = adx
    out["di_diff"] = plus_di - minus_di
    
    out["candle_body"] = (close - open_p) / (high - low).replace(0, np.nan)
    out["upper_wick"] = (high - pd.concat([open_p, close], axis=1).max(axis=1)) / (high - low).replace(0, np.nan)
    out["lower_wick"] = (pd.concat([open_p, close], axis=1).min(axis=1) - low) / (high - low).replace(0, np.nan)
    
    out["return_1"] = close.pct_change(1)
    out["return_3"] = close.pct_change(3)
    return out

def build_labels(df, horizon=1):
    close = df["Close"]
    future_return = close.shift(-horizon) / close - 1
    label = (future_return > 0).astype(int)
    return label, future_return

# ──────────────────────────────────────────────────────────────
# 5) 3-AI ENSEMBLE VOTING ENGINE
# ──────────────────────────────────────────────────────────────

def train_and_evaluate(features, labels, test_size=0.25):
    from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier, VotingClassifier
    from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score

    data = features.copy()
    data["label"] = labels
    data = data.dropna()

    split_idx = int(len(data) * (1 - test_size))
    train, test = data.iloc[:split_idx], data.iloc[split_idx:]

    feat_cols = [c for c in data.columns if c != "label"]
    X_train, y_train = train[feat_cols], train["label"]
    X_test, y_test = test[feat_cols], test["label"]

    # Sadexda AI ee kala duwan oo isku darsanaya awooddooda (Voting Ensemble)
    model1 = RandomForestClassifier(n_estimators=150, max_depth=6, min_samples_leaf=20, random_state=42, n_jobs=1)
    model2 = ExtraTreesClassifier(n_estimators=150, max_depth=6, min_samples_leaf=20, random_state=42, n_jobs=1)
    model3 = GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42)

    model = VotingClassifier(
        estimators=[('rf', model1), ('et', model2), ('gb', model3)],
        voting='soft'
    )
    
    model.fit(X_train, y_train)

    proba_test = model.predict_proba(X_test)[:, 1]
    pred_test = (proba_test >= 0.5).astype(int)

    metrics = {
        "accuracy": accuracy_score(y_test, pred_test),
        "precision": precision_score(y_test, pred_test, zero_division=0),
        "recall": recall_score(y_test, pred_test, zero_division=0),
    }
    try:
        metrics["roc_auc"] = roc_auc_score(y_test, proba_test)
    except ValueError:
        metrics["roc_auc"] = float("nan")

    return model, feat_cols, X_test, y_test, proba_test, metrics

def accuracy_by_confidence(y_test, proba_test, thresholds):
    rows = []
    for t in thresholds:
        buy_mask = proba_test >= t
        sell_mask = proba_test <= (1 - t)
        mask = buy_mask | sell_mask
        n = mask.sum()
        if n == 0:
            continue
        pred = np.where(buy_mask[mask], 1, 0)
        actual = y_test[mask].values
        acc = (pred == actual).mean()
        rows.append({
            "Confidence Level": f"{int(t*100)}%+",
            "Filtered Trades": int(n),
            "Accuracy Natiijo": f"{acc * 100:.1f}%"
        })
    return pd.DataFrame(rows)

# ──────────────────────────────────────────────────────────────
# 6) STREAMLIT UI DESIGN (3-AI ENSEMBLE + MTF)
# ──────────────────────────────────────────────────────────────

st.title("🔬 PROV MAHAD - 3-AI ENSEMBLE ELITE BOT")
st.caption("Real Market Binary Engine (3-AI Voting Ensemble + Price Action + MTF + News Filter)")

news_data = fetch_news_calendar()

with st.sidebar:
    st.header("⚙️ Nidaamka Isku-dubbaridda")
    pair_name = st.selectbox("1. Dooro Lacagta (Pair)", list(PAIRS.keys()))
    interval = st.selectbox("2. Dooro Waqtiga (Timeframe)", ["3m", "5m", "15m", "1h"], index=0)
    
    st.write("---")
    st.subheader("🛠️ Advanced Settings")
    predict_horizon = st.slider("Predict Horizon (N Candles)", min_value=1, max_value=5, value=1, step=1)
    test_size_pct = st.slider("Test Size (%)", min_value=10, max_value=50, value=25, step=5) / 100.0
    
    st.write("---")
    train_btn = st.button("🚀 GET 3-AI ENSEMBLE SIGNAL")
    
    st.write("---")
    st.info("""
    * **3-AI Voting**: Sadex Algorithms ayaa isla ogolaada signal-ka.
    * **MTF Filter**: Jihada 1-Hour ayaa xukunta guud ahaan nidaamka.
    """)

if train_btn:
    upcoming_events, is_high_risk = check_pair_news(news_data, pair_name)
    if is_high_risk:
        st.error(f"🚨 **DIGNIIN NEWS ADAG:** Pair-kan ({pair_name}) wuxuu leeyahay warar High-Impact ah!")
    elif upcoming_events:
        st.warning(f"⚠️ **DIGNIIN NEWS:** Waxaa jira warar Medium-Impact ah oo ku dhow pair-kan:")
        for ev in upcoming_events:
            st.write(f"• **{ev['country']} - {ev['title']}** ({ev['impact']}) - Time: {ev['time']}")

    macro_trend = get_macro_trend(PAIRS[pair_name])
    st.info(f"🌐 **Multi-Timeframe Macro Trend (1H):** {macro_trend}")

    with st.spinner("3-da AI ee kala duwan ayaa falanqeynaya suuqa (Ensemble Voting)..."):
        try:
            raw = fetch_data(PAIRS[pair_name], interval)
        except Exception as e:
            st.error(f"Cilad ayaa dhacday: {e}")
            st.stop()

    if raw.empty or len(raw) < 200:
        st.error("Xog ku filan lama helin. Isku day Timeframe kale.")
        st.stop()

    feats = build_features(raw)
    labels, future_ret = build_labels(raw, horizon=predict_horizon) 

    model, feat_cols, X_test, y_test, proba_test, metrics = train_and_evaluate(feats, labels, test_size=test_size_pct)

    st.subheader("🔮 3-AI ENSEMBLE LIVE SIGNAL")
    latest_feats = feats.dropna().iloc[[-1]]
    latest_price = raw["Close"].iloc[-1]
    
    if not latest_feats.empty:
        latest_proba = model.predict_proba(latest_feats[feat_cols])[0, 1]
        sig = "BUY (CALL)" if latest_proba >= 0.5 else "SELL (PUT)"
        conf = latest_proba if sig == "BUY (CALL)" else 1 - latest_proba
        
        mtf_conflict = False
        if "BULLISH" in macro_trend and sig == "SELL (PUT)":
            mtf_conflict = True
        elif "BEARISH" in macro_trend and sig == "BUY (CALL)":
            mtf_conflict = True

        col1, col2, col3 = st.columns(3)
        col1.metric("📊 SIGNAL-KA", sig)
        col2.metric("🎯 3-AI CONFIDENCE", f"{conf*100:.1f}%")
        col3.metric("💰 QIIMAHA HADA", f"{latest_price:.5f}")
        
        auc = metrics["roc_auc"]
        if is_high_risk:
            st.error("⛔ **TALO:** Suuqu wuxuu ku jiraa saameyn warar ah, ka fogow trade-kan!")
        elif mtf_conflict:
            st.error(f"⚠️ **MTF CONFLICT WARNING:** Signal-kani ({sig}) wuxuu ka horjeedaa macro trend-ka 1H ({macro_trend}).")
        elif pd.isna(auc) or auc < 0.55:
            st.error(f"⚠️ **Digniin:** Model-ka ROC-AUC-giisu waa hooseeyaa ({auc:.3f}).")
        elif conf < 0.70:
            st.warning(f"⚠️ **Fariin:** Kalsoonida 3-AI waa {conf*100:.1f}% (Ka hooseysa 70%). Sug fursad xoog badan.")
        else:
            st.success(f"🚀 **3-AI ENSEMBLE SIGNAL OOGAN:** Sadexda AI waxay isla garteen signal-kan oo kalsoonidiisu tahay ({conf*100:.1f}%)!")

    st.divider()

    st.subheader("📊 Tayada Model-ka (3-AI Validation)")
    col_acc, col_auc, col_prec = st.columns(3)
    col_acc.metric("🎯 Accuracy Guud", f"{metrics['accuracy']*100:.1f}%")
    col_auc.metric("📉 ROC-AUC", f"{metrics['roc_auc']:.3f}")
    col_prec.metric("📈 Precision", f"{metrics['precision']*100:.1f}%")

    st.divider()

    st.subheader("🎯 Jadwalka Saxnaanta Heerarka Kalsoonida (Confidence Matrix)")
    thresh_df = accuracy_by_confidence(y_test.reset_index(drop=True), proba_test, [0.5, 0.6, 0.7, 0.8])
    if not thresh_df.empty:
        st.dataframe(thresh_df, use_container_width=True, hide_index=True)
    else:
        st.write("Xog ku filan jadwalka lama hayo hadda.")

else:
    st.info("Dooro Pair iyo Timeframe dhanka bidix ah, ka dibna riix badanka '🚀 GET 3-AI ENSEMBLE SIGNAL'.")
