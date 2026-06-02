import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

# ----------------------------------------------------
# 1. BOT ENGINE CONFIGURATION (ULTIMATE FILTER LOGIC)
# ----------------------------------------------------
class ProAnalystBot:
    def __init__(self, symbol, timeframe):
        self.symbol = symbol
        self.timeframe = timeframe

    def calculate_indicators(self, df):
        # 1. Xisaabinta EMA 50 ee Jihada Suuqa (Trend Filter)
        df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()

        # 2. Xisaabinta RSI 14 (Overbought/Oversold Filter)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 0.00001)
        df['RSI_14'] = 100 - (100 / (1 + rs))
        return df

    def analyze_patterns(self, df):
        if len(df) < 50:  # Waxaan u baahannahay ugu yaraan 50 shumac si EMA 50 u xisaabto
            return {"Action": "HOLD", "Pattern": "Xog ku yar suuqa (Sug inta ay 50 shumac ka dhalanayso)"}

        df = self.calculate_indicators(df)

        # Soo jiid xogta shumacyadii ugu dambeeyey iyo indicators-ka
        try:
            c_open = float(df['Open'].iloc[-1].item()) if hasattr(df['Open'].iloc[-1], 'item') else float(df['Open'].iloc[-1])
            c_close = float(df['Close'].iloc[-1].item()) if hasattr(df['Close'].iloc[-1], 'item') else float(df['Close'].iloc[-1])
            c_high = float(df['High'].iloc[-1].item()) if hasattr(df['High'].iloc[-1], 'item') else float(df['High'].iloc[-1])
            c_low = float(df['Low'].iloc[-1].item()) if hasattr(df['Low'].iloc[-1], 'item') else float(df['Low'].iloc[-1])
            
            p_open = float(df['Open'].iloc[-2].item()) if hasattr(df['Open'].iloc[-2], 'item') else float(df['Open'].iloc[-2])
            p_close = float(df['Close'].iloc[-2].item()) if hasattr(df['Close'].iloc[-2], 'item') else float(df['Close'].iloc[-2])
            p_high = float(df['High'].iloc[-2].item()) if hasattr(df['High'].iloc[-2], 'item') else float(df['High'].iloc[-2])
            p_low = float(df['Low'].iloc[-2].item()) if hasattr(df['Low'].iloc[-2], 'item') else float(df['Low'].iloc[-2])
            
            current_ema = float(df['EMA_50'].iloc[-1].item()) if hasattr(df['EMA_50'].iloc[-1], 'item') else float(df['EMA_50'].iloc[-1])
            current_rsi = float(df['RSI_14'].iloc[-1].item()) if hasattr(df['RSI_14'].iloc[-1], 'item') else float(df['RSI_14'].iloc[-1])
        except:
            c_open = float(df['Open'].values[-1])
            c_close = float(df['Close'].values[-1])
            c_high = float(df['High'].values[-1])
            c_low = float(df['Low'].values[-1])
            
            p_open = float(df['Open'].values[-2])
            p_close = float(df['Close'].values[-2])
            p_high = float(df['High'].values[-2])
            p_low = float(df['Low'].values[-2])
            
            current_ema = float(df['EMA_50'].values[-1])
            current_rsi = float(df['RSI_14'].values[-1])

        c_body = abs(c_close - c_open)
        c_total_range = (c_high - c_low) if (c_high - c_low) > 0 else 0.0001

        # Xeerarka Jihada Suuqa (Trend Confirmation)
        is_uptrend = c_close > current_ema
        is_downtrend = c_close < current_ema

        # Candlestick Logic
        is_doji = c_body <= (c_total_range * 0.1)
        c_upper_wick = c_high - max(c_open, c_close)
        c_lower_wick = min(c_open, c_close) - c_low
        
        is_hammer = (c_lower_wick >= c_body * 2) and (c_upper_wick <= c_body * 0.5)
        is_shooting_star = (c_upper_wick >= c_body * 2) and (c_lower_wick <= c_body * 0.5)
        is_bullish_engulfing = (p_close < p_open) and (c_close > c_open) and (c_close >= p_open) and (c_open <= p_close)
        is_bearish_engulfing = (p_close > p_open) and (c_close < c_open) and (c_close <= p_open) and (c_open >= p_close)

        signal = {"Action": "HOLD", "Pattern": "Suuq caadi ah (No High-Probability Setup)"}

        # ---- STRATEGY 1: BULLISH ENTRIES (KALIYA MARKUU UPTREND JIRO + RSI SANAD TAHAY) ----
        if (is_hammer or is_bullish_engulfing):
            if is_uptrend:
                if current_rsi < 70:  # Iska ilaali iibsashada haddii suuqu aad u sarreeyo
                    signal["Action"] = "BUY"
                    signal["Pattern"] = f"{'Hammer' if is_hammer else 'Bullish Engulfing'} + Ka sarreeya EMA50 (Uptrend Confirmation) + RSI: {current_rsi:.1f}"
                else:
                    signal["Action"] = "WAIT"
                    signal["Pattern"] = f"Waxaa dhashay Bullish Pattern laakiin Suuqa baa aad u sarreeya (RSI Overbought: {current_rsi:.1f}). Halis weyn!"
            else:
                signal["Action"] = "WAIT"
                signal["Pattern"] = "Bullish Pattern baa dhashay laakiin Jihada suuqu waa hoos (Below EMA50). Signal-ka waa la baajiyey."

        # ---- STRATEGY 2: BEARISH ENTRIES (KALIYA MARKUU DOWNTREND JIRO + RSI SANAD TAHAY) ----
        elif (is_shooting_star or is_bearish_engulfing):
            if is_downtrend:
                if current_rsi > 30:  # Iska ilaali iibinta haddii suuqu aad u hooseeyo
                    signal["Action"] = "SELL"
                    signal["Pattern"] = f"{'Shooting Star' if is_shooting_star else 'Bearish Engulfing'} + Ka hooseeya EMA50 (Downtrend Confirmation) + RSI: {current_rsi:.1f}"
                else:
                    signal["Action"] = "WAIT"
                    signal["Pattern"] = f"Waxaa dhashay Bearish Pattern laakiin Suuqa baa aad u hooseeya (RSI Oversold: {current_rsi:.1f}). Halis weyn!"
            else:
                signal["Action"] = "WAIT"
                signal["Pattern"] = "Bearish Pattern baa dhashay laakiin Jihada suuqu waa kor (Above EMA50). Signal-ka waa la baajiyey."
                
        elif is_doji:
            signal["Action"] = "WAIT"
            signal["Pattern"] = f"Doji Found. Suuqu go'aan ma laha. RSI: {current_rsi:.1f}"

        return signal

# ----------------------------------------------------
# 2. STREAMLIT INTERFACE UI DESIGN
# ----------------------------------------------------
st.set_page_config(page_title="Mahad AI - Pro Version", layout="centered")

st.title("🤖 Mahad AI - PRO V2 (Trend & RSI Filtered)")
st.write("Kani waa nooca labaad ee bot-kaaga oo hadda leh filter-ro adag si looga fogaado signals-ka beenta ah.")
st.markdown("---")

st.subheader("⚙️ Dejinta Suuqa")

asset_map = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X",
    "AUD/USD": "AUDUSD=X", "AUD/CHF": "AUDCHF=X", "AUD/JPY": "AUDJPY=X",
    "AUD/NZD": "AUDNZD=X", "CAD/CHF": "CADCHF=X", "CAD/JPY": "CADJPY=X",
    "CHF/JPY": "CHFJPY=X", "EUR/AUD": "EURAUD=X", "EUR/CAD": "EURCAD=X",
    "EUR/CHF": "EURCHF=X", "EUR/GBP": "EURGBP=X", "EUR/JPY": "EURJPY=X",
    "EUR/NZD": "EURNZD=X", "GBP/AUD": "GBPAUD=X", "GBP/CAD": "GBPCAD=X",
    "GBP/CHF": "GBPCHF=X", "GBP/NZD": "GBPNZD=X", "NZD/CAD": "NZDCAD=X",
    "NZD/CHF": "NZDCHF=X", "NZD/JPY": "NZDJPY=X", "NZD/USD": "NZDUSD=X",
    "USD/CAD": "CAD=X", "USD/CHF": "CHF=X"
}

asset_choice = st.selectbox("Dooro Lacagta (Asset):", list(asset_map.keys()))
timeframe = st.selectbox("Dooro Waqtiga (Timeframe):", ["1m", "2m"])

ticker_symbol = asset_map[asset_choice]

st.markdown("---")
st.subheader("🚨 Ogeysiiska Fursadaha Tooska Ah")

if st.button("Kici Live Scanner-ka 🔄"):
    with st.spinner("Bot-ku wuxuu falanqaynayaa EMA50 iyo RSI..."):
        try:
            # Waxaan soo jiideynaa xog ku filan (period="5d") si ay indicators-ku u xisaabshaan qaab sax ah
            data = yf.download(tickers=ticker_symbol, period="5d", interval=timeframe, group_by="ticker")
            
            if not data.empty:
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.get_level_values(-1)
                
                last_close_series = data['Close'].squeeze()
                current_price = float(last_close_series.iloc[-1])
                
                st.metric(label=f"Qiimaha Live-ka ah ee {asset_choice}", value=f"{current_price:.5f}")
                
                bot = ProAnalystBot(symbol=asset_choice, timeframe=timeframe)
                result = bot.analyze_patterns(data)
                
                # Bandhigga Natiijada iyadoo loo eegayo badbaadada
                if result["Action"] == "BUY":
                    st.success(f"🟢 **{result['Action']} SIGNAL FOUND! (High Probability)**")
                    st.info(f"**Sababta:** {result['Pattern']}")
                elif result["Action"] == "SELL":
                    st.error(f"🔴 **{result['Action']} SIGNAL FOUND! (High Probability)**")
                    st.info(f"**Sababta:** {result['Pattern']}")
                elif result["Action"] == "WAIT":
                    st.warning(f"🟡 **SNAKED/WAIT:** {result['Pattern']}")
                else:
                    st.info(f"⚪ **HOLD:** {result['Pattern']}")
            else:
                st.error("Xogta suuqa waa la waayay.")
        except Exception as e:
            st.error(f"Cillad ayaa dhacday: {e}")
