import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import json
from datetime import datetime

# ── STREAMLIT PAGE CONFIG ──────────────────────────────────────────────────
st.set_page_config(
    page_title="MAHAD SIGNALS PRO",
    page_icon="⚡",
    layout="wide"
)

# ── SUPPRESS STREAMLIT DEFAULT UI (Qari walxaha dabiiciga ah ee Streamlit) ──
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 1rem; max-width: 480px; margin: 0 auto;}
    [data-testid="stSidebar"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# ── LIST OF 15 REAL PAIRS (Code-kii 2-aad) ──────────────────────────────────
PAIRS = [
    'EURUSD', 'EURJPY', 'EURCHF', 'EURCAD', 'EURAUD',
    'AUDUSD', 'AUDJPY', 'AUDCHF', 'AUDCAD',
    'CADCHF', 'CADJPY', 'CHFJPY',
    'USDCAD', 'USDCHF', 'USDJPY'
]

# ── URL QUERY STATE FOR INTERACTION ─────────────────────────────────────────
if "tf" not in st.query_params:
    st.query_params["tf"] = "3m"
if "min_conf" not in st.query_params:
    st.query_params["min_conf"] = "60"

current_tf = st.query_params["tf"]
current_min_conf = int(st.query_params["min_conf"])

# ── INTERACTION REGISTRATION INTERFACE ──────────────────────────────────────
# Controls (Khadka doorashada Timeframe iyo Confidence)
col1, col2 = st.columns(2)
with col1:
    tf_options = {"1m": "1 min", "3m": "3 min", "5m": "5 min", "10m": "10 min", "15m": "15 min"}
    selected_tf = st.selectbox("Timeframe", list(tf_options.keys()), format_func=lambda x: tf_options[x], index=list(tf_options.keys()).index(current_tf))
with col2:
    conf_options = [50, 60, 70, 80]
    selected_conf = st.selectbox("Min Confidence", conf_options, format_func=lambda x: f"{x}%+", index=conf_options.index(current_min_conf))

if selected_tf != current_tf or selected_conf != current_min_conf:
    st.query_params["tf"] = selected_tf
    st.query_params["min_conf"] = str(selected_conf)
    st.rerun()

# ── FAST DATA FETCH ENGINE (No Twelve Data Delay) ──────────────────────────
def get_crypto_or_fx_data(pair, tf):
    ticker = f"{pair}=X"
    fetch_tf = "1m" if tf in ["1m", "3m", "5m"] else ("5m" if tf == "10m" else "15m")
    period = "2d" if fetch_tf == "1m" else "5d"
    
    try:
        df = yf.Ticker(ticker).history(period=period, interval=fetch_tf)
        if df.empty or len(df) < 30:
            return None
        
        # Resampling matching code 2's interval logic
        if tf == "3m":
            df = df.resample("3min").agg({"Open":"first","High":"max","Low":"min","Close":"last","Volume":"sum"}).dropna()
        elif tf == "10m":
            df = df.resample("10min").agg({"Open":"first","High":"max","Low":"min","Close":"last","Volume":"sum"}).dropna()
            
        return {
            "close": df["Close"].tolist(),
            "high": df["High"].tolist(),
            "low": df["Low"].tolist(),
            "open": df["Open"].tolist()
        }
    except:
        return None

# ── ALL 7 TECHNICAL INDICATORS & SCORES FROM CODE 2 ────────────────────────
def analyze_signal(ohlc):
    close = pd.Series(ohlc["close"])
    high = pd.Series(ohlc["high"])
    low = pd.Series(ohlc["low"])
    
    price = close.iloc[-1]
    
    # 1. RSI
    rsi_s = ta.rsi(close, length=14)
    rsi = rsi_s.iloc[-1] if rsi_s is not None else 50
    
    # 2. MACD
    macd_df = ta.macd(close, fast=12, slow=26, signal=9)
    macd_hist = macd_df.iloc[-1, 1] if macd_df is not None else 0
    
    # 3. Bollinger Bands
    bb = ta.bbands(close, length=20, std=2)
    bb_low = bb.iloc[-1, 0] if bb is not None else price
    bb_up = bb.iloc[-1, 2] if bb is not None else price
    
    # 4. Stochastic
    stoch_df = ta.stoch(high, low, close, k=14, d=3)
    stoch = stoch_df.iloc[-1, 0] if stoch_df is not None else 50
    
    # 5. Parabolic SAR
    psar = ta.psar(high, low, close)
    psar_rising = True
    if psar is not None:
        psar_cols = psar.columns.tolist()
        psar_rising = pd.isna(psar.iloc[-1][psar_cols[1]]) # If falling is NaN, it's rising
        
    # 6. ADX
    adx_df = ta.adx(high, low, close, length=14)
    adx = adx_df.iloc[-1, 0] if adx_df is not None else 20
    
    # 7. EMAs (5, 10, 20)
    ema5 = ta.ema(close, length=5).iloc[-1]
    ema10 = ta.ema(close, length=10).iloc[-1]
    ema20 = ta.ema(close, length=20).iloc[-1]
    
    buy_score = 0
    sell_score = 0
    buy_inds = []
    sell_inds = []
    
    # RSI Logic
    if rsi < 30: buy_score += 2; buy_inds.append('RSI OB')
    elif rsi < 45: buy_score += 1; buy_inds.append('RSI↑')
    elif rsi > 70: sell_score += 2; sell_inds.append('RSI OS')
    elif rsi > 55: sell_score += 1; sell_inds.append('RSI↓')
    
    # MACD Logic
    if macd_hist > 0: buy_score += 1.5; buy_inds.append('MACD')
    else: sell_score += 1.5; sell_inds.append('MACD')
    
    # BB Logic
    if price < bb_low: buy_score += 2; buy_inds.append('BB↑')
    elif price > bb_up: sell_score += 2; sell_inds.append('BB↓')
    
    # Stoch Logic
    if stoch < 20: buy_score += 1.5; buy_inds.append('STOCH')
    elif stoch > 80: sell_score += 1.5; sell_inds.append('STOCH')
    
    # PSAR Logic
    if psar_rising: buy_score += 1.5; buy_inds.append('PSAR')
    else: sell_score += 1.5; sell_inds.append('PSAR')
    
    # EMA Trend Logic
    if ema5 > ema10 and ema10 > ema20: buy_score += 2; buy_inds.append('EMA↑')
    elif ema5 < ema10 and ema10 < ema20: sell_score += 2; sell_inds.append('EMA↓')
    
    # ADX Trend Strength Multiplier
    trend_strength = 1.3 if adx > 25 else (1.1 if adx > 20 else 0.9)
    buy_score *= trend_strength
    sell_score *= trend_strength
    
    total = buy_score + sell_score
    confidence = round((max(buy_score, sell_score) / total * 100 * 0.6) + 40) if total > 0 else 50
    capped_conf = min(95, max(50, confidence))
    
    diff = buy_score - sell_score
    if diff > 4: signal_type = 'strong-buy'; direction = 'buy'
    elif diff > 1.5: signal_type = 'buy'; direction = 'buy'
    elif diff < -4: signal_type = 'strong-sell'; direction = 'sell'
    elif diff < -1.5: signal_type = 'sell'; direction = 'sell'
    else: signal_type = 'neutral'; direction = 'neutral'
    
    return {
        "price": price,
        "rsi": round(rsi, 1),
        "signal": signal_type,
        "direction": direction,
        "confidence": capped_conf,
        "adx": round(adx, 1),
        "buyInds": buy_inds,
        "sellInds": sell_inds
    }

# ── RUN CONCURRENT SCAN ON BUTTON CLICK ─────────────────────────────────────
signals_data = []
buys_count = 0
sells_count = 0

if st.button("⚡ SCAN ALL PAIRS", use_container_width=True):
    for pair in PAIRS:
        ohlc = get_crypto_or_fx_data(pair, current_tf)
        if ohlc:
            analysis = analyze_signal(ohlc)
            if analysis["confidence"] >= current_min_conf:
                analysis["pair"] = f"{pair[:3]}/{pair[3:]}"
                signals_data.append(analysis)
                if analysis["direction"] == "buy": buys_count += 1
                if analysis["direction"] == "sell": sells_count += 1

# ── RENDER EXACT THEME HTML/CSS VISUALIZER ──────────────────────────────────
# Halkan waxaa lagu shubayaa dhamaan CSS-tii quruxda badnayd iyo qaab dhismeedka code-kaaga labaad
html_template = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
  
  :root {{
    --bg: #080c10; --surface: #0d1117; --card: #111820; --border: #1e2d3d;
    --accent: #00d4ff; --accent2: #0099cc; --buy: #00e676; --buy-dim: #00e67620;
    --sell: #ff3d57; --sell-dim: #ff3d5720; --neutral: #ffa726; --neutral-dim: #ffa72620;
    --text: #e0eaf5; --text-dim: #8899aa; --strong: #ffffff;
  }}
  body {{ background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; }}
  .header {{ padding: 10px 0; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border); margin-bottom: 16px; }}
  .logo {{ font-family: 'Rajdhani', sans-serif; font-size: 22px; font-weight: 700; letter-spacing: 2px; background: linear-gradient(90deg, var(--accent), #7b61ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
  .status-dot {{ display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--text-dim); font-family: 'Share Tech Mono', monospace; }}
  .dot {{ width: 8px; height: 8px; border-radius: 50%; background: var(--buy); box-shadow: 0 0 8px var(--buy); }}
  .stats-row {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 16px; }}
  .stat-box {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 10px; text-align: center; }}
  .stat-val {{ font-family: 'Rajdhani', sans-serif; font-size: 20px; font-weight: 700; color: var(--strong); }}
  .stat-lbl {{ font-size: 10px; color: var(--text-dim); text-transform: uppercase; }}
  .signal-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 14px; margin-bottom: 10px; position: relative; }}
  .signal-card::before {{ content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; }}
  .signal-card.buy::before, .signal-card.strong-buy::before {{ background: var(--buy); }}
  .signal-card.sell::before, .signal-card.strong-sell::before {{ background: var(--sell); }}
  .signal-card.neutral::before {{ background: var(--neutral); }}
  .card-top {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }}
  .pair-name {{ font-family: 'Rajdhani', sans-serif; font-size: 18px; font-weight: 700; color: var(--strong); }}
  .signal-badge {{ padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; text-transform: uppercase; }}
  .badge-strong-buy {{ background: var(--buy-dim); color: var(--buy); border: 1px solid var(--buy); }}
  .badge-buy {{ background: var(--buy-dim); color: var(--buy); border: 1px solid #00e67650; }}
  .badge-strong-sell {{ background: var(--sell-dim); color: var(--sell); border: 1px solid var(--sell); }}
  .badge-sell {{ background: var(--sell-dim); color: var(--sell); border: 1px solid #ff3d5750; }}
  .badge-neutral {{ background: var(--neutral-dim); color: var(--neutral); border: 1px solid #ffa72650; }}
  .card-mid {{ display: flex; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; }}
  .info-chip {{ background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 4px 9px; font-size: 11px; color: var(--text-dim); font-family: 'Share Tech Mono', monospace; }}
  .info-chip span {{ color: var(--text); }}
  .conf-row {{ display: flex; align-items: center; gap: 8px; }}
  .conf-label {{ font-size: 10px; color: var(--text-dim); width: 70px; }}
  .conf-bar-bg {{ flex: 1; height: 5px; background: var(--border); border-radius: 5px; overflow: hidden; }}
  .conf-bar-fill {{ height: 100%; border-radius: 5px; }}
  .conf-val {{ font-family: 'Share Tech Mono', monospace; font-size: 12px; color: var(--strong); width: 35px; text-align: right; }}
  .indicators-row {{ display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px; }}
  .ind-tag {{ font-size: 9px; padding: 2px 6px; border-radius: 4px; font-family: 'Share Tech Mono', monospace; }}
  .ind-buy {{ background: #00e67615; color: #00e676; }}
  .ind-sell {{ background: #ff3d5715; color: #ff3d57; }}
  .empty {{ text-align: center; padding: 40px 20px; color: var(--text-dim); }}
  .empty-icon {{ font-size: 36px; margin-bottom: 10px; }}
  .last-update {{ text-align: center; font-size: 10px; color: var(--text-dim); font-family: 'Share Tech Mono', monospace; margin-top: 10px; }}
</style>
</head>
<body>
  <div class="header">
    <div class="logo">MAHAD SIGNALS</div>
    <div class="status-dot"><div class="dot"></div><span>LIVE ENGINE</span></div>
  </div>

  <div class="stats-row">
    <div class="stat-box"><div class="stat-val" style="color:var(--buy);">{buys_count}</div><div class="stat-lbl">BUY</div></div>
    <div class="stat-box"><div class="stat-val" style="color:var(--sell);">{sells_count}</div><div class="stat-lbl">SELL</div></div>
    <div class="stat-box"><div class="stat-val">{len(signals_data)}</div><div class="stat-lbl">SIGNALS</div></div>
  </div>

  <div style="font-size: 11px; color: var(--text-dim); letter-spacing: 1.5px; margin-bottom: 10px;">SIGNALS</div>
  <div id="signalsList">
"""

if not signals_data:
    html_template += f"""
    <div class="empty">
      <div class="empty-icon">📡</div>
      <div class="empty-text">Press <b>⚡ SCAN ALL PAIRS</b> above to fetch live signals.<br>Timeframe: {tf_options[current_tf]} | Filter: {current_min_conf}%+</div>
    </div>
    """
else:
    for s in signals_data:
        signal_label = s["signal"].replace('-', ' ').toUpperCase() if hasattr(str, 'toUpperCase') else s["signal"].replace('-', ' ').upper()
        conf_color = '#00e676' if s["confidence"] >= 80 else ('#ffa726' if s["confidence"] >= 65 else '#8899aa')
        
        buy_tags = "".join([f'<span class="ind-tag ind-buy">{i}</span>' for i in s["buyInds"]])
        sell_tags = "".join([f'<span class="ind-tag ind-sell">{i}</span>' for i in s["sellInds"]])
        
        html_template += f"""
        <div class="signal-card {s["signal"]}">
          <div class="card-top">
            <div class="pair-name">{s["pair"]}</div>
            <div class="signal-badge badge-{s["signal"]}">{signal_label}</div>
          </div>
          <div class="card-mid">
            <div class="info-chip">Price <span>{s["price"]:.5f}</span></div>
            <div class="info-chip">RSI <span>{s["rsi"]}</span></div>
            <div class="info-chip">ADX <span>{s["adx"]}</span></div>
            <div class="info-chip">Expiry <span>{tf_options[current_tf]}</span></div>
          </div>
          <div class="conf-row">
            <div class="conf-label">Confidence</div>
            <div class="conf-bar-bg">
              <div class="conf-bar-fill" style="width:{s["confidence"]}%; background:{conf_color};"></div>
            </div>
            <div class="conf-val">{s["confidence"]}%</div>
          </div>
          <div class="indicators-row">
            {buy_tags}{sell_tags}
          </div>
        </div>
        """

html_template += f"""
  </div>
  <div class="last-update">Last fast scan: {datetime.now().strftime('%H:%M:%S')} — Expiry matched to Timeframe</div>
</body>
</html>
"""

# Render the UI seamlessly inside Streamlit
st.components.v1.html(html_template, height=800, scroller=True)
