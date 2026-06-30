import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
from datetime import datetime

# ── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(page_title="MAHAD SIGNALS PRO", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 1rem; max-width: 480px; margin: 0 auto;}
    [data-testid="stSidebar"] {display: none;}
    div.stButton > button {
        background: linear-gradient(135deg, #0099cc, #7b61ff);
        color: white;
        font-weight: 700;
        font-size: 16px;
        letter-spacing: 2px;
        border: none;
        border-radius: 10px;
        padding: 13px;
        width: 100%;
    }
    div.stButton > button:hover { opacity: 0.85; }
    </style>
""", unsafe_allow_html=True)

# ── PAIRS ──────────────────────────────────────────────────────────────────
PAIRS = [
    'EURUSD', 'EURJPY', 'EURCHF', 'EURCAD', 'EURAUD',
    'AUDUSD', 'AUDJPY', 'AUDCHF', 'AUDCAD',
    'CADCHF', 'CADJPY', 'CHFJPY',
    'USDCAD', 'USDCHF', 'USDJPY'
]

TF_OPTIONS = {"1m": "1 min", "3m": "3 min", "5m": "5 min", "10m": "10 min", "15m": "15 min"}
EXPIRY_MAP = {"1m": "1 min", "3m": "3 min", "5m": "5 min", "10m": "10 min", "15m": "15 min"}

# ── SESSION STATE ──────────────────────────────────────────────────────────
if "tf_state" not in st.session_state:
    st.session_state.tf_state = "3m"
if "conf_state" not in st.session_state:
    st.session_state.conf_state = 60

# ── CONTROLS ───────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    selected_tf = st.selectbox(
        "Timeframe",
        list(TF_OPTIONS.keys()),
        format_func=lambda x: TF_OPTIONS[x],
        index=list(TF_OPTIONS.keys()).index(st.session_state.tf_state)
    )
with col2:
    conf_options = [50, 60, 70, 80]
    selected_conf = st.selectbox(
        "Min Confidence",
        conf_options,
        format_func=lambda x: f"{x}%+",
        index=conf_options.index(st.session_state.conf_state)
    )

if selected_tf != st.session_state.tf_state or selected_conf != st.session_state.conf_state:
    st.session_state.tf_state = selected_tf
    st.session_state.conf_state = selected_conf
    st.rerun()

# ── DATA FETCH ─────────────────────────────────────────────────────────────
def get_ohlc(pair, tf):
    """
    FIX 1: Timezone-ka si sax ah loo xukumo
    FIX 2: Resample si sax ah
    FIX 3: Min candles 50 (halkii 30)
    """
    ticker = f"{pair}=X"

    # Map UI timeframe → Yahoo fetch interval
    if tf in ["1m", "3m"]:
        fetch_interval = "1m"
        period = "2d"
    elif tf == "5m":
        fetch_interval = "5m"
        period = "5d"
    elif tf == "10m":
        fetch_interval = "5m"
        period = "5d"
    else:  # 15m
        fetch_interval = "15m"
        period = "5d"

    try:
        df = yf.Ticker(ticker).history(period=period, interval=fetch_interval)
        if df is None or df.empty or len(df) < 50:
            return None

        # FIX 1: Ka saar timezone si resample u shaqeeyo
        if df.index.tz is not None:
            df.index = df.index.tz_convert("UTC").tz_localize(None)

        # FIX 2: Resample haddii loo baahdo
        if tf == "3m":
            df = df.resample("3min").agg({
                "Open": "first", "High": "max",
                "Low": "min", "Close": "last", "Volume": "sum"
            }).dropna()
        elif tf == "10m":
            df = df.resample("10min").agg({
                "Open": "first", "High": "max",
                "Low": "min", "Close": "last", "Volume": "sum"
            }).dropna()

        if len(df) < 30:
            return None

        return {
            "close": df["Close"].tolist(),
            "high": df["High"].tolist(),
            "low": df["Low"].tolist(),
            "open": df["Open"].tolist()
        }
    except Exception:
        return None

# ── SIGNAL ANALYSIS ────────────────────────────────────────────────────────
def analyze_signal(ohlc):
    """
    FIX 3: MACD histogram column name-ka si sax ah lagu helo
    FIX 4: Bollinger Bands column name-ka si sax ah
    FIX 5: Parabolic SAR logic sax ah
    FIX 6: ADX score thresholds hagaajin
    FIX 7: Score diff thresholds hoos u dhig (signals badan)
    """
    try:
        close = pd.Series(ohlc["close"], dtype=float)
        high  = pd.Series(ohlc["high"],  dtype=float)
        low   = pd.Series(ohlc["low"],   dtype=float)

        if len(close) < 30:
            return None

        price = close.iloc[-1]

        # 1. RSI
        rsi_s = ta.rsi(close, length=14)
        rsi = float(rsi_s.iloc[-1]) if rsi_s is not None and not rsi_s.empty else 50.0

        # 2. MACD — FIX 3: column name-ka si sax ah
        macd_df = ta.macd(close, fast=12, slow=26, signal=9)
        macd_hist = 0.0
        if macd_df is not None and not macd_df.empty:
            hist_cols = [c for c in macd_df.columns if 'MACDh' in c or 'Histogram' in c.lower()]
            if hist_cols:
                macd_hist = float(macd_df[hist_cols[0]].iloc[-1])
            else:
                # Fallback: index 1
                macd_hist = float(macd_df.iloc[-1, 1])

        # 3. Bollinger Bands — FIX 4: column name sax
        bb = ta.bbands(close, length=20, std=2)
        bb_low_val = price
        bb_up_val  = price
        if bb is not None and not bb.empty:
            bbl_cols = [c for c in bb.columns if 'BBL' in c]
            bbu_cols = [c for c in bb.columns if 'BBU' in c]
            if bbl_cols:
                bb_low_val = float(bb[bbl_cols[0]].iloc[-1])
            if bbu_cols:
                bb_up_val = float(bb[bbu_cols[0]].iloc[-1])

        # 4. Stochastic
        stoch_df = ta.stoch(high, low, close, k=14, d=3)
        stoch = 50.0
        if stoch_df is not None and not stoch_df.empty:
            k_cols = [c for c in stoch_df.columns if 'STOCHk' in c or 'K' in c]
            if k_cols:
                stoch = float(stoch_df[k_cols[0]].iloc[-1])
            else:
                stoch = float(stoch_df.iloc[-1, 0])

        # 5. Parabolic SAR — FIX 5: logic sax
        psar_rising = True
        psar_df = ta.psar(high, low, close)
        if psar_df is not None and not psar_df.empty:
            long_cols  = [c for c in psar_df.columns if 'PSARl' in c]
            short_cols = [c for c in psar_df.columns if 'PSARs' in c]
            if long_cols:
                # Rising = PSARl column-ku waa NaN marka trending down
                psar_rising = not pd.isna(psar_df[long_cols[0]].iloc[-1])
            elif short_cols:
                psar_rising = pd.isna(psar_df[short_cols[0]].iloc[-1])

        # 6. ADX — FIX 6: column name sax
        adx = 20.0
        adx_df = ta.adx(high, low, close, length=14)
        if adx_df is not None and not adx_df.empty:
            adx_cols = [c for c in adx_df.columns if 'ADX' in c and 'DM' not in c]
            if adx_cols:
                adx = float(adx_df[adx_cols[0]].iloc[-1])
            else:
                adx = float(adx_df.iloc[-1, 0])
        adx = min(90.0, max(8.0, adx))  # Cap realistic

        # 7. EMAs
        ema5  = float(ta.ema(close, length=5).iloc[-1])
        ema10 = float(ta.ema(close, length=10).iloc[-1])
        ema20 = float(ta.ema(close, length=20).iloc[-1])

        # ── SCORING ───────────────────────────────────────────────────────
        buy_score  = 0.0
        sell_score = 0.0
        buy_inds   = []
        sell_inds  = []

        # RSI
        if rsi < 30:
            buy_score += 2; buy_inds.append('RSI OB')
        elif rsi < 45:
            buy_score += 1; buy_inds.append('RSI↑')
        elif rsi > 70:
            sell_score += 2; sell_inds.append('RSI OS')
        elif rsi > 55:
            sell_score += 1; sell_inds.append('RSI↓')

        # MACD
        if macd_hist > 0:
            buy_score += 1.5; buy_inds.append('MACD')
        else:
            sell_score += 1.5; sell_inds.append('MACD')

        # Bollinger
        if price < bb_low_val:
            buy_score += 2; buy_inds.append('BB↑')
        elif price > bb_up_val:
            sell_score += 2; sell_inds.append('BB↓')

        # Stochastic
        if stoch < 20:
            buy_score += 1.5; buy_inds.append('STOCH')
        elif stoch > 80:
            sell_score += 1.5; sell_inds.append('STOCH')

        # Parabolic SAR
        if psar_rising:
            buy_score += 1.5; buy_inds.append('PSAR')
        else:
            sell_score += 1.5; sell_inds.append('PSAR')

        # EMA trend
        if ema5 > ema10 and ema10 > ema20:
            buy_score += 2; buy_inds.append('EMA↑')
        elif ema5 < ema10 and ema10 < ema20:
            sell_score += 2; sell_inds.append('EMA↓')

        # ADX trend strength multiplier
        trend_strength = 1.3 if adx > 25 else (1.1 if adx > 20 else 0.9)
        buy_score  *= trend_strength
        sell_score *= trend_strength

        # Confidence
        total = buy_score + sell_score
        confidence = round((max(buy_score, sell_score) / total * 100 * 0.6) + 40) if total > 0 else 50
        capped_conf = min(95, max(50, confidence))

        # FIX 7: Thresholds hoos u dhig — signals badan
        diff = buy_score - sell_score
        if diff > 3:
            signal_type = 'strong-buy';  direction = 'buy'
        elif diff > 1:
            signal_type = 'buy';         direction = 'buy'
        elif diff < -3:
            signal_type = 'strong-sell'; direction = 'sell'
        elif diff < -1:
            signal_type = 'sell';        direction = 'sell'
        else:
            signal_type = 'neutral';     direction = 'neutral'

        return {
            "price":     price,
            "rsi":       round(rsi, 1),
            "signal":    signal_type,
            "direction": direction,
            "confidence": capped_conf,
            "adx":       round(adx, 1),
            "buyInds":   buy_inds,
            "sellInds":  sell_inds
        }
    except Exception:
        return None

# ── SCAN BUTTON ────────────────────────────────────────────────────────────
signals_data = []
buys_count   = 0
sells_count  = 0
scan_time    = ""

if st.button("⚡ SCAN ALL PAIRS", use_container_width=True):
    with st.spinner("Scanning 15 pairs..."):
        for pair in PAIRS:
            ohlc = get_ohlc(pair, st.session_state.tf_state)
            if ohlc is None:
                continue
            analysis = analyze_signal(ohlc)
            if analysis is None:
                continue
            if analysis["confidence"] >= st.session_state.conf_state:
                analysis["pair"] = f"{pair[:3]}/{pair[3:]}"
                signals_data.append(analysis)
                if analysis["direction"] == "buy":
                    buys_count += 1
                if analysis["direction"] == "sell":
                    sells_count += 1

    # Sort by confidence descending
    signals_data.sort(key=lambda x: x["confidence"], reverse=True)
    scan_time = datetime.now().strftime('%H:%M:%S')

# ── RENDER HTML ────────────────────────────────────────────────────────────
tf_label = TF_OPTIONS[st.session_state.tf_state]
expiry   = EXPIRY_MAP[st.session_state.tf_state]

if not signals_data:
    html_cards = f"""
    <div class="empty">
      <div class="empty-icon">📡</div>
      <div class="empty-text">Press <b>⚡ SCAN ALL PAIRS</b> to fetch live signals.<br>
      Timeframe: {tf_label} | Filter: {st.session_state.conf_state}%+</div>
    </div>
    """
else:
    html_cards = ""
    for s in signals_data:
        signal_label = s["signal"].replace('-', ' ').upper()
        conf_color = (
            '#00e676' if s["confidence"] >= 80 else
            '#ffa726' if s["confidence"] >= 65 else
            '#8899aa'
        )
        buy_tags  = "".join([f'<span class="ind-tag ind-buy">{i}</span>'  for i in s["buyInds"]])
        sell_tags = "".join([f'<span class="ind-tag ind-sell">{i}</span>' for i in s["sellInds"]])

        html_cards += f"""
        <div class="signal-card {s['signal']}">
          <div class="card-top">
            <div class="pair-name">{s['pair']}</div>
            <div class="signal-badge badge-{s['signal']}">{signal_label}</div>
          </div>
          <div class="card-mid">
            <div class="info-chip">Price <span>{s['price']:.5f}</span></div>
            <div class="info-chip">RSI <span>{s['rsi']}</span></div>
            <div class="info-chip">ADX <span>{s['adx']}</span></div>
            <div class="info-chip">Expiry <span>{expiry}</span></div>
          </div>
          <div class="conf-row">
            <div class="conf-label">Confidence</div>
            <div class="conf-bar-bg">
              <div class="conf-bar-fill" style="width:{s['confidence']}%; background:{conf_color};"></div>
            </div>
            <div class="conf-val">{s['confidence']}%</div>
          </div>
          <div class="indicators-row">{buy_tags}{sell_tags}</div>
        </div>
        """

last_scan_line = f'<div class="last-update">Last scan: {scan_time} — TF: {tf_label} — Expiry: {expiry}</div>' if scan_time else ''

html_template = f"""
<!DOCTYPE html><html><head>
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@700&family=Inter:wght@400;600&display=swap');
:root {{
  --bg:#080c10; --card:#111820; --border:#1e2d3d; --surface:#0d1117;
  --accent:#00d4ff; --buy:#00e676; --buy-dim:#00e67620;
  --sell:#ff3d57; --sell-dim:#ff3d5720; --neutral:#ffa726; --neutral-dim:#ffa72620;
  --text:#e0eaf5; --text-dim:#8899aa; --strong:#ffffff;
}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;padding:0 4px;}}
.header{{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--border);padding:12px 0;margin-bottom:14px;}}
.logo{{font-family:'Rajdhani',sans-serif;font-size:22px;font-weight:700;letter-spacing:2px;background:linear-gradient(90deg,var(--accent),#7b61ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.dot-row{{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--text-dim);font-family:'Share Tech Mono',monospace;}}
.dot{{width:8px;height:8px;border-radius:50%;background:var(--buy);box-shadow:0 0 8px var(--buy);}}
.stats-row{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:14px;}}
.stat-box{{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:10px;text-align:center;}}
.stat-val{{font-family:'Rajdhani',sans-serif;font-size:20px;font-weight:700;}}
.stat-lbl{{font-size:10px;color:var(--text-dim);text-transform:uppercase;}}
.sec-title{{font-size:11px;color:var(--text-dim);letter-spacing:1.5px;text-transform:uppercase;margin-bottom:10px;}}
.signal-card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px;margin-bottom:10px;position:relative;overflow:hidden;}}
.signal-card::before{{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;border-radius:3px 0 0 3px;}}
.signal-card.buy::before,.signal-card.strong-buy::before{{background:var(--buy);}}
.signal-card.sell::before,.signal-card.strong-sell::before{{background:var(--sell);}}
.signal-card.neutral::before{{background:var(--neutral);}}
.card-top{{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;}}
.pair-name{{font-family:'Rajdhani',sans-serif;font-size:18px;font-weight:700;color:var(--strong);}}
.signal-badge{{padding:4px 12px;border-radius:20px;font-size:11px;font-weight:600;letter-spacing:1px;text-transform:uppercase;}}
.badge-strong-buy{{background:var(--buy-dim);color:var(--buy);border:1px solid var(--buy);}}
.badge-buy{{background:var(--buy-dim);color:var(--buy);border:1px solid #00e67650;}}
.badge-strong-sell{{background:var(--sell-dim);color:var(--sell);border:1px solid var(--sell);}}
.badge-sell{{background:var(--sell-dim);color:var(--sell);border:1px solid #ff3d5750;}}
.badge-neutral{{background:var(--neutral-dim);color:var(--neutral);border:1px solid #ffa72650;}}
.card-mid{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px;}}
.info-chip{{background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:4px 9px;font-size:11px;color:var(--text-dim);font-family:'Share Tech Mono',monospace;}}
.info-chip span{{color:var(--text);}}
.conf-row{{display:flex;align-items:center;gap:8px;}}
.conf-label{{font-size:10px;color:var(--text-dim);width:70px;}}
.conf-bar-bg{{flex:1;height:5px;background:var(--border);border-radius:5px;overflow:hidden;}}
.conf-bar-fill{{height:100%;border-radius:5px;}}
.conf-val{{font-family:'Share Tech Mono',monospace;font-size:12px;color:var(--strong);width:35px;text-align:right;}}
.indicators-row{{display:flex;flex-wrap:wrap;gap:4px;margin-top:8px;}}
.ind-tag{{font-size:9px;padding:2px 6px;border-radius:4px;font-family:'Share Tech Mono',monospace;}}
.ind-buy{{background:#00e67615;color:#00e676;}}
.ind-sell{{background:#ff3d5715;color:#ff3d57;}}
.empty{{text-align:center;padding:40px 20px;color:var(--text-dim);}}
.empty-icon{{font-size:36px;margin-bottom:10px;}}
.empty-text{{font-size:13px;line-height:1.7;}}
.last-update{{text-align:center;font-size:10px;color:var(--text-dim);font-family:'Share Tech Mono',monospace;margin-top:12px;padding-bottom:20px;}}
</style>
</head>
<body>
<div class="header">
  <div class="logo">MAHAD SIGNALS</div>
  <div class="dot-row"><div class="dot"></div><span>LIVE</span></div>
</div>
<div class="stats-row">
  <div class="stat-box"><div class="stat-val" style="color:var(--buy);">{buys_count}</div><div class="stat-lbl">BUY</div></div>
  <div class="stat-box"><div class="stat-val" style="color:var(--sell);">{sells_count}</div><div class="stat-lbl">SELL</div></div>
  <div class="stat-box"><div class="stat-val">{len(signals_data)}</div><div class="stat-lbl">SIGNALS</div></div>
</div>
<div class="sec-title">SIGNALS</div>
{html_cards}
{last_scan_line}
</body></html>
"""

st.components.v1.html(html_template, height=900, scrolling=True)
