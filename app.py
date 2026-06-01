import streamlit as st
import pandas as pd
import numpy as np

# ----------------------------------------------------
# 1. BOT ENGINE CONFIGURATION (PRO ANALYST LOGIC)
# ----------------------------------------------------
class ProAnalystBot:
    def __init__(self, symbol, timeframe):
        self.symbol = symbol
        self.timeframe = timeframe

    def analyze_patterns(self, df):
        if len(df) < 2:
            return {"Asset": self.symbol, "Timeframe": self.timeframe, "Action": "HOLD", "Pattern": "Xogta ku yar"}

        # Shumacyada hadda jooga
        c_open = df['open'].iloc[-1]
        c_close = df['close'].iloc[-1]
        c_high = df['high'].iloc[-1]
        c_low = df['low'].iloc[-1]
        
        p_open = df['open'].iloc[-2]
        p_close = df['close'].iloc[-2]
        p_high = df['high'].iloc[-2]
        p_low = df['low'].iloc[-2]

        c_body = abs(c_close - c_open)
        c_total_range = (c_high - c_low) if (c_high - c_low) > 0 else 0.0001

        # 1. Candlestick Patterns
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

        # Output Object
        signal = {"Asset": self.symbol, "Timeframe": self.timeframe, "Action": "HOLD", "Pattern": "Suuq caadi ah (No Pattern)"}

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
# 2. STREAMLIT INTERFACE UI DESIGN
# ----------------------------------------------------
st.set_page_config(page_title="Mahad AI - Pro Scanner", layout="centered")

st.title("🤖 Mahad AI - Pro Scanner Bot")
st.write("Kani waa bot-ka falanqaynta tooska ah ee ku dhex baari lahaa suuqyada Real iyo OTC.")
st.markdown("---")

# Qaybta Doorashada Suuqyada (Sidebar ama Main Page)
st.subheader("⚙️ Dejinta Scanner-ka")
asset_name = st.selectbox("Dooro Lacagta (Asset):", ["EUR/USD", "GBP/USD", "EUR/USD_OTC", "USD/JPY_OTC"])
timeframe = st.selectbox("Dooro Waqtiga (Timeframe):", ["15s", "30s", "1m", "2m"])

# --- SHUMACYAHA TIJAABADA AH (Waxaad badali kartaa si aad u tijaabiso) ---
st.subheader("📊 Geli Qiimaha Shumaca Hadda (Tijaabo)")
col1, col2, col3, col4 = st.columns(4)
with col1: o_val = st.number_input("Open Price", value=1.1000, format="%.4f")
with col2: h_val = st.number_input("High Price", value=1.1030, format="%.4f")
with col3: l_val = st.number_input("Low Price", value=1.0980, format="%.4f")
with col4: c_val = st.number_input("Close Price", value=1.1025, format="%.4f")

# Xogta loo dirayo Bot-ka (Shumacii hore iyo Kan hadda)
mock_data = {
    'open':  [1.1020, o_val],
    'high':  [1.1025, h_val],
    'low':   [1.1000, l_val],
    'close': [1.1005, c_val] # Shumaca hore waa Casraan, Kan hadda adigaa xakameynaya
}
df_market = pd.DataFrame(mock_data)

# ----------------------------------------------------
# 3. SIGNAL DISPLAY LOGIC
# ----------------------------------------------------
st.markdown("---")
st.subheader("🚨 Ogeysiiska Fursadaha Live-ka ah")

if st.button("Run Scanner 🔍"):
    bot = ProAnalystBot(symbol=asset_name, timeframe=timeframe)
    result = bot.analyze_patterns(df_market)
    
    # Sida ay shaashadda ugu soo baxayso iyadoo midabaysan
    if result["Action"] == "BUY":
        st.success(f"🟢 **{result['Action']} SIGNAL FOUND!**")
        st.metric(label="Asset & Timeframe", value=f"{result['Asset']} ({result['Timeframe']})")
        st.info(f"**Pattern:** {result['Pattern']}")
        
    elif result["Action"] == "SELL":
        st.error(f"🔴 **{result['Action']} SIGNAL FOUND!**")
        st.metric(label="Asset & Timeframe", value=f"{result['Asset']} ({result['Timeframe']})")
        st.info(f"**Pattern:** {result['Pattern']}")
        
    elif result["Action"] == "WAIT":
        st.warning(f"🟡 **WAIT:** {result['Pattern']}")
        
    else:
        st.info("⚪ **HOLD:** Suuqyada la baaray hadda lagama helin wax qaab ah. Sug shumaca xiga.")
