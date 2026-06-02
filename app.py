import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

# ----------------------------------------------------
# 1. INSTITUTIONAL BOT ENGINE (BOLLINGER + MACD)
# ----------------------------------------------------
class InstitutionalMomentumBot:
    def __init__(self, symbol, timeframe_choice):
        self.symbol = symbol
        self.timeframe_choice = timeframe_choice

    def resample_data(self, df, minutes):
        """Xogta 1m ayuu u beddelayaa waqtiyada kale oo nadiif ah"""
        resample_str = f"{minutes}min"
        resampled = df.resample(resample_str).agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()
        return resampled

    def calculate_indicators(self, df):
        # 1. Bollinger Bands (20, 2)
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['STD'] = df['Close'].rolling(window=20).std()
        df['Upper_Band'] = df['MA20'] + (df['STD'] * 2)
        df['Lower_Band'] = df['MA20'] - (df['STD'] * 2)

        # 2. MACD (12, 26, 9)
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        return df

    def analyze_market(self, df):
        if self.timeframe_choice in ["4m", "10m"]:
            minutes = 4 if self.timeframe_choice == "4m" else 10
            df = self.resample_data(df, minutes)
            
        df = self.calculate_indicators(df)

        if len(df) < 30:
            return {"Action": "HOLD", "Pattern": "Xogtu ku yar tahay indicator-rada (Sug xoogaa)"}

        try:
            c_close = float(df['Close'].iloc[-1].item()) if hasattr(df['Close'].iloc[-1], 'item') else float(df['Close'].iloc[-1])
            c_upper = float(df['Upper_Band'].iloc[-1].item()) if hasattr(df['Upper_Band'].iloc[-1], 'item') else float(df['Upper_Band'].iloc[-1])
            c_lower = float(df['Lower_Band'].iloc[-1].item()) if hasattr(df['Lower_Band'].iloc[-1], 'item') else float(df['Lower_Band'].iloc[-1])
            
            c_macd = float(df['MACD'].iloc[-1].item()) if hasattr(df['MACD'].iloc[-1], 'item') else float(df['MACD'].iloc[-1])
            c_signal = float(df['Signal_Line'].iloc[-1].item()) if hasattr(df['Signal_Line'].iloc[-1], 'item') else float(df['Signal_Line'].iloc[-1])
            
            p_macd = float(df['MACD'].iloc[-2].item()) if hasattr(df['MACD'].iloc[-2], 'item') else float(df['MACD'].iloc[-2])
            p_signal = float(df['Signal_Line'].iloc[-2].item()) if hasattr(df['Signal_Line'].iloc[-2], 'item') else float(df['Signal_Line'].iloc[-2])
        except:
            c_close = float(df['Close'].values[-1])
            c_upper = float(df['Upper_Band'].values[-1])
            c_lower = float(df['Lower_Band'].values[-1])
            c_macd = float(df['MACD'].values[-1])
            c_signal = float(df['Signal_Line'].values[-1])
            p_macd = float(df['MACD'].values[-2])
            p_signal = float(df['Signal_Line'].values[-2])

        # Shuruudaha Xoogga Suuqa (Momentum Rules)
        macd_bullish_cross = (c_macd > c_signal) and (p_macd <= p_signal)
        macd_bearish_cross = (c_macd < c_signal) and (p_macd >= p_signal)
        macd_is_bullish = c_macd > c_signal
        macd_is_bearish = c_macd < c_signal

        signal = {"Action": "HOLD", "Pattern": "Suuq meel dhexe taagan (No Institutional Volatility)"}

        # ---- STRATEGY: STRONGBULL BREAKOUT (BUY) ----
        if c_close >= c_upper or (c_close > (c_upper * 0.999) and macd_bullish_cross):
            if macd_is_bullish:
                signal["Action"] = "BUY"
                signal["Pattern"] = f"Institutional Volatility Breakout! Qiimuhu wuxuu jabiyey Upper Bollinger Band + MACD Bullish Jihaysan."
            else:
                signal["Action"] = "WAIT"
                signal["Pattern"] = "Qiimuhu waa sareeyaa laakiin awoodda MACD ma taageersana (Divergence Risk)."

        # ---- STRATEGY: STRONGBEAR BREAKOUT (SELL) ----
        elif c_close <= c_lower or (c_close < (c_lower * 1.001) and macd_bearish_cross):
            if macd_is_bearish:
                signal["Action"] = "SELL"
                signal["Pattern"] = f"Institutional Volatility Breakdown! Qiimuhu wuxuu hoos u dhaafay Lower Bollinger Band + MACD Bearish Jihaysan."
            else:
                signal["Action"] = "WAIT"
                signal["Pattern"] = "Qiimuhu waa hooseeyaa laakiin awoodda MACD ma taageersana (Fakeout Risk)."
                
        # ---- SQUEEZE DETECTION (NO TRADE ZONE) ----
        elif abs(c_upper - c_lower) < (c_close * 0.001):
            signal["Action"] = "WAIT"
            signal["Pattern"] = "Suuqu aad ayuu u dhuubtay (Bollinger Squeeze). Bangiyadu trade ma galayaan hadda."

        return signal

# ----------------------------------------------------
# 2. STREAMLIT INTERFACE UI DESIGN
# ----------------------------------------------------
st.set_page_config(page_title="Mahad AI - Institutional", layout="centered")

st.title("🤖 Mahad AI - INSTITUTIONAL EDITION (V4)")
st.write("Kani waa bot ku shaqeeya algorithms-ka maamula awoodda iyo dhaqdhaqaaqa waaweyn ee suuqa.")
st.markdown("---")

st.subheader("⚙️ Dejinta Suuqa")

asset_map = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X", 
    "EUR/JPY": "EURJPY=X", "GBP/JPY": "GBPJPY=X", "AUD/USD": "AUDUSD=X", 
    "USD/CAD": "CAD=X", "USD/CHF": "CHF=X", "AUD/JPY": "AUDJPY=X"
}

asset_choice = st.selectbox("Dooro Lacagta (Asset):", sorted(list(asset_map.keys())))
tf_choice = st.selectbox("Dooro Waqtiga (Timeframe):", ["4m", "5m", "10m", "15m"])

ticker_symbol = asset_map[asset_choice]

st.markdown("---")
st.subheader("🚨 Ogeysiiska Fursadaha Tooska Ah")

if st.button("Kici Institutional Scanner-ka 🔄"):
    with st.spinner(f"Bot-ku wuxuu xisaabinayaa Bollinger Bands & MACD ee {tf_choice}..."):
        try:
            download_tf = "1m" if tf_choice in ["4m", "10m"] else tf_choice
            data = yf.download(tickers=ticker_symbol, period="5d", interval=download_tf, group_by="ticker")
            
            if not data.empty:
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.get_level_values(-1)
                
                last_close_series = data['Close'].squeeze()
                current_price = float(last_close_series.iloc[-1])
                
                st.metric(label=f"Qiimaha Live-ka ah ee {asset_choice}", value=f"{current_price:.5f}")
                
                bot = InstitutionalMomentumBot(symbol=asset_choice, timeframe_choice=tf_choice)
                result = bot.analyze_market(data)
                
                if result["Action"] == "BUY":
                    st.success(f"🟢 **{result['Action']} SIGNAL FOUND! (Institutional Quality)**")
                    st.info(f"**Xogta Farsamada:** {result['Pattern']}")
                elif result["Action"] == "SELL":
                    st.error(f"🔴 **{result['Action']} SIGNAL FOUND! (Institutional Quality)**")
                    st.info(f"**Xogta Farsamada:** {result['Pattern']}")
                elif result["Action"] == "WAIT":
                    st.warning(f"🟡 **HOLD / WAIT:** {result['Pattern']}")
                else:
                    st.info(f"⚪ **HOLD:** {result['Pattern']}")
            else:
                st.error("Xogta suuqa waa la waayay.")
        except Exception as e:
            st.error(f"Cillad ayaa dhacday: {e}")
