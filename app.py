import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import time

# ----------------------------------------------------
# 1. BOT ENGINE LOGIC
# ----------------------------------------------------
class ProAnalystBot:
    def __init__(self, symbol, timeframe):
        self.symbol = symbol
        self.timeframe = timeframe

    def analyze_patterns(self, df):
        if len(df) < 5:
            return {"Action": "HOLD", "Pattern": "Xog ku yar suuqa"}

        # Shumacyada ugu dambeeyey ee live-ka ah
        c_open = df['Open'].iloc[-1]
        c_close = df['Close'].iloc[-1]
        c_high = df['High'].iloc[-1]
        c_low = df['Low'].iloc[-1]
        
        p_open = df['Open'].iloc[-2]
        p_close = df['Close'].iloc[-2]
        p_high = df['High'].iloc[-2]
        p_low = df['Low'].iloc[-2]

        c_body = abs(c_close - c_open)
        c_total_range = (c_high - c_low) if (c_high - c_low) > 0 else 0.0001

        # 1. Candlestick Psychology Algorithms
        is_doji = c_body <= (c_total_range * 0.1)

        c_upper_wick = c_high - max(c_open, c_close)
        c_lower_wick = min(c_open, c_close) - c_low
        is_hammer = (c_lower_wick >= c_body * 2) and (c_upper_wick <= c_body * 0.5)
        is_shooting_star = (c_upper_wick >= c_body * 2) and (c_lower_wick <= c_body * 0.5)

        is_bullish_engulfing = (p_close < p_open) and (c_close > c_open) and (c_close >= p_open) and (c_open <= p_close)
        is_bearish_engulfing = (p_close > p_open) and (c_close < c_open) and (c_close <= p_open) and (c_open >= p_close)

        p_midpoint = p_open + (p_close - p_open) / 2
        is_piercing_line = (p_close < p_open) and (c_open < p_close) and (c_close > p_midpoint) and (c_close < p_open)
        is_dark_cloud = (p_close > p_open) and (c_open > p_close) and (c_close < p_midpoint) and (c_close > p_open)

        is_tweezer_bottom = (p_close < p_open) and (c_close > c_open) and abs(p_low - c_low) <= (c_low * 0.0001)
        is_tweezer_top = (p_close > p_open) and (c_close < c_open) and abs(p_high - c_high) <= (c_high * 0.0001)

        signal = {"Action": "HOLD", "Pattern": "Suuq caadi ah (No Pattern)"}

        if is_hammer or is_bullish_engulfing or is_piercing_line or is_tweezer_bottom:
            signal["Action"] = "BUY"
            if is_hammer: signal["Pattern"] = "Hammer Found (Support Zone)"
            elif is_bullish_engulfing: signal["Pattern"] = "Bullish Engulfing"
            elif is_piercing_line: signal["Pattern"] = "Piercing Line (Gap Down + 50%)"
            elif is_tweezer_bottom: signal["Pattern"] = "Tweezer Bottoms"

        elif is_shooting_star or is_bearish_engulfing or is_dark_cloud or is_tweezer_top:
            signal["Action"] = "SELL"
            if is_shooting_star: signal["Pattern"] = "Shooting Star Found (Resistance Zone)"
            elif is_bearish_engulfing: signal["Pattern"] = "Bearish Engulfing"
            elif is_dark_cloud: signal["Pattern"] = "Dark Cloud Cover (Gap Up + 50%)"
            elif is_tweezer_top: signal["Pattern"] = "Tweezer Tops"
            
        elif is_doji:
            signal["Action"] = "WAIT"
            signal["Pattern"] = "Doji (Sug Confirmation)"

        return signal

# ----------------------------------------------------
# 2. STREAMLIT INTERFACE
# ----------------------------------------------------
st.set_page_config(page_title="Mahad AI - Live Scanner", layout="centered")

st.title("🤖 Mahad AI - Live Scanner Bot")
st.write("Kani waa bot-ka oo hadda xogta live-ka ah si otomaatig ah u soo jiidaya.")
st.markdown("---")

st.subheader("⚙️ Dejinta Suuqa")

# Khariidadda loogu talagalay yfinance symbols (Real Forex)
asset_map = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X",
    "AUD/USD": "AUDUSD=X"
}

asset_choice = st.selectbox("Dooro Lacagta (Asset):", list(asset_map.keys()))
# 1m iyo 2m ayaa ah kuwa ugu yar ee yfinance uu oggol yahay live-ka
timeframe = st.selectbox("Dooro Waqtiga (Timeframe):", ["1m", "2m"])

ticker_symbol = asset_map[asset_choice]

st.markdown("---")
st.subheader("🚨 Ogeysiiska Fursadaha Live-ka ah")

# Badanka lagu kiciyo scanner-ka live-ka ah
if st.button("Kici Live Scanner-ka 🔄"):
    with st.spinner("Bot-ku wuxuu soo jiidayaa xogta suuqa dhabta ah..."):
        try:
            # Soo jiid xogta 5-tii shumac ee u dambeeyey
            data = yf.download(tickers=ticker_symbol, period="1d", interval=timeframe)
            
            if not data.empty:
                # Muuji qiimaha ugu dambeeyey ee live-ka ah ee suuqa
                current_price = data['Close'].iloc[-1]
                st.metric(label=f"Qiimaha Live-ka ah ee {asset_choice}", value=f"{current_price:.5f}")
                
                # Falanqaynta bot-ka
                bot = ProAnalystBot(symbol=asset_choice, timeframe=timeframe)
                result = bot.analyze_patterns(data)
                
                # Bandhigga Natiijada
                if result["Action"] == "BUY":
                    st.success(f"🟢 **{result['Action']} SIGNAL FOUND!**")
                    st.info(f"**Pattern:** {result['Pattern']}")
                elif result["Action"] == "SELL":
                    st.error(f"🔴 **{result['Action']} SIGNAL FOUND!**")
                    st.info(f"**Pattern:** {result['Pattern']}")
                elif result["Action"] == "WAIT":
                    st.warning(f"🟡 **WAIT:** {result['Pattern']}")
                else:
                    st.info(f"⚪ **HOLD:** {result['Pattern']}. Shumaca hadda socda ma dhalin wax qaab ah.")
            else:
                st.error("Waqtigaan suuqu waa xiran yahay ama xogta waa la waayay.")
        except Exception as e:
            st.error(f"Cillad ayaa dhacday: {e}")
