import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

# ----------------------------------------------------
# 1. BOT ENGINE CONFIGURATION (RESAMPLING & FILTERS)
# ----------------------------------------------------
class UltimateMultiTimeframeBot:
    def __init__(self, symbol, timeframe_choice):
        self.symbol = symbol
        self.timeframe_choice = timeframe_choice

    def resample_data(self, df, minutes):
        """Xogta 1m ayuu u beddelayaa 4m ama 10m oo nadiif ah"""
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
        # 1. EMA 50 ee Jihada Suuqa (Trend Filter)
        df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()

        # 2. RSI 14 (Overbought/Oversold Filter)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 0.00001)
        df['RSI_14'] = 100 - (100 / (1 + rs))
        return df

    def analyze_patterns(self, df):
        if self.timeframe_choice in ["4m", "10m"]:
            minutes = 4 if self.timeframe_choice == "4m" else 10
            df = self.resample_data(df, minutes)
            
        df = self.calculate_indicators(df)

        if len(df) < 20:
            return {"Action": "HOLD", "Pattern": "Xog ku yar suuqa timeframe-kan (Sug xoogaa)"}

        try:
            c_open = float(df['Open'].iloc[-1].item()) if hasattr(df['Open'].iloc[-1], 'item') else float(df['Open'].iloc[-1])
            c_close = float(df['Close'].iloc[-1].item()) if hasattr(df['Close'].iloc[-1], 'item') else float(df['Close'].iloc[-1])
            c_high = float(df['High'].iloc[-1].item()) if hasattr(df['High'].iloc[-1], 'item') else float(df['High'].iloc[-1])
            c_low = float(df['Low'].iloc[-1].item()) if hasattr(df['Low'].iloc[-1], 'item') else float(df['Low'].iloc[-1])
            
            p_open = float(df['Open'].iloc[-2].item()) if hasattr(df['Open'].iloc[-2], 'item') else float(df['Open'].iloc[-2])
            p_close = float(df['Close'].iloc[-2].item()) if hasattr(df['Close'].iloc[-2], 'item') else float(df['Close'].iloc[-2])
            
            current_ema = float(df['EMA_50'].iloc[-1].item()) if hasattr(df['EMA_50'].iloc[-1], 'item') else float(df['EMA_50'].iloc[-1])
            current_rsi = float(df['RSI_14'].iloc[-1].item()) if hasattr(df['RSI_14'].iloc[-1], 'item') else float(df['RSI_14'].iloc[-1])
        except:
            c_open = float(df['Open'].values[-1])
            c_close = float(df['Close'].values[-1])
            c_high = float(df['High'].values[-1])
            c_low = float(df['Low'].values[-1])
            
            p_open = float(df['Open'].values[-2])
            p_close = float(df['Close'].values[-2])
            
            current_ema = float(df['EMA_50'].values[-1])
            current_rsi = float(df['RSI_14'].values[-1])

        c_body = abs(c_close - c_open)
        c_total_range = (c_high - c_low) if (c_high - c_low) > 0 else 0.0001

        # Trend and Candlestick Logic
        is_uptrend = c_close > current_ema
        is_downtrend = c_close < current_ema

        c_upper_wick = c_high - max(c_open, c_close)
        c_lower_wick = min(c_open, c_close) - c_low
        
        is_hammer = (c_lower_wick >= c_body * 2) and (c_upper_wick <= c_body * 0.5)
        is_shooting_star = (c_upper_wick >= c_body * 2) and (c_lower_wick <= c_body * 0.5)
        is_bullish_engulfing = (p_close < p_open) and (c_close > c_open) and (c_close >= p_open) and (c_open <= p_close)
        is_bearish_engulfing = (p_close > p_open) and (c_close < c_open) and (c_close <= p_open) and (c_open >= p_close)

        signal = {"Action": "HOLD", "Pattern": f"Suuq caadi ah (No Trend Setup on {self.timeframe_choice})"}

        # ---- BUY STRATEGY ----
        if (is_hammer or is_bullish_engulfing):
            if is_uptrend:
                if current_rsi < 68:
                    signal["Action"] = "BUY"
                    signal["Pattern"] = f"{'Hammer' if is_hammer else 'Bullish Engulfing'} + Uptrend Confirmed + RSI: {current_rsi:.1f}"
                else:
                    signal["Action"] = "WAIT"
                    signal["Pattern"] = f"Bullish Pattern dhashay laakiin suuqu waa koreeyaa (RSI Overbought: {current_rsi:.1f})"
            else:
                signal["Action"] = "WAIT"
                signal["Pattern"] = "Pattern-ku waa BUY laakiin Jihada guud waa SELL (Below EMA50)."

        # ---- SELL STRATEGY ----
        elif (is_shooting_star or is_bearish_engulfing):
            if is_downtrend:
                if current_rsi > 32:
                    signal["Action"] = "SELL"
                    signal["Pattern"] = f"{'Shooting Star' if is_shooting_star else 'Bearish Engulfing'} + Downtrend Confirmed + RSI: {current_rsi:.1f}"
                else:
                    signal["Action"] = "WAIT"
                    signal["Pattern"] = f"Bearish Pattern dhashay laakiin suuqu waa hooseeyaa (RSI Oversold: {current_rsi:.1f})"
            else:
                signal["Action"] = "WAIT"
                signal["Pattern"] = "Pattern-ku waa SELL laakiin Jihada guud waa BUY (Above EMA50)."

        return signal

# ----------------------------------------------------
# 2. STREAMLIT INTERFACE UI DESIGN (ALL FOREX PAIRS)
# ----------------------------------------------------
st.set_page_config(page_title="Mahad AI - Ultimate V3", layout="centered")

st.title("🤖 Mahad AI - MULTI-TIMEFRAME V3")
st.write("Kani waa nooca dhammaystiran oo xalay la ballaariyey dhammaan Pairs-ka Forex ee rasmiga ah.")
st.markdown("---")

st.subheader("⚙️ Dejinta Suuqa")

# Dhammaan lacagaha oo dhammaystiran (38 Pairs)
asset_map = {
    # Euro Crosses
    "EUR/USD": "EURUSD=X", "EUR/GBP": "EURGBP=X", "EUR/JPY": "EURJPY=X", 
    "EUR/CHF": "EURCHF=X", "EUR/CAD": "EURCAD=X", "EUR/AUD": "EURAUD=X", 
    "EUR/NZD": "EURNZD=X",
    
    # Great Britain Pound Crosses
    "GBP/USD": "GBPUSD=X", "GBP/JPY": "GBPJPY=X", "GBP/CHF": "GBPCHF=X", 
    "GBP/CAD": "GBPCAD=X", "GBP/AUD": "GBPAUD=X", "GBP/NZD": "GBPNZD=X",
    
    # US Dollar Majors & Minors
    "USD/JPY": "JPY=X", "USD/CHF": "CHF=X", "USD/CAD": "CAD=X", 
    "USD/SGD": "USDSGD=X", "USD/HKD": "USDHKD=X", "USD/TRY": "USDTRY=X", 
    "USD/ZAR": "USDZAR=X", "USD/MXN": "USDMXN=X",
    
    # Australian Dollar Crosses
    "AUD/USD": "AUDUSD=X", "AUD/JPY": "AUDJPY=X", "AUD/CHF": "AUDCHF=X", 
    "AUD/CAD": "AUDCAD=X", "AUD/NZD": "AUDNZD=X",
    
    # New Zealand Dollar Crosses
    "NZD/USD": "NZDUSD=X", "NZD/JPY": "NZDJPY=X", "NZD/CHF": "NZDCHF=X", 
    "NZD/CAD": "NZDCAD=X",
    
    # Canadian Dollar & Swiss Franc Crosses
    "CAD/JPY": "CADJPY=X", "CAD/CHF": "CADCHF=X", "CHF/JPY": "CHFJPY=X",
    
    # Exotic/Other Pairs (Kuwa mararka qaar Pocket Option bixiyo)
    "SGD/JPY": "SGDJPY=X", "GBP/SGD": "GBPSGD=X", "EUR/SGD": "EURSGD=X",
    "AUD/SGD": "AUDSGD=X", "EUR/HKD": "EURHKD=X"
}

asset_choice = st.selectbox("Dooro Lacagta (Asset):", sorted(list(asset_map.keys())))
tf_choice = st.selectbox("Dooro Waqtiga (Timeframe):", ["4m", "5m", "10m", "15m"])

ticker_symbol = asset_map[asset_choice]

st.markdown("---")
st.subheader("🚨 Ogeysiiska Fursadaha Tooska Ah")

if st.button("Kici Live Scanner-ka 🔄"):
    with st.spinner(f"Bot-ku wuxuu isu diyaarinayaa falanqaynta {tf_choice}..."):
        try:
            download_tf = "1m" if tf_choice in ["4m", "10m"] else tf_choice
            
            data = yf.download(tickers=ticker_symbol, period="5d", interval=download_tf, group_by="ticker")
            
            if not data.empty:
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.get_level_values(-1)
                
                last_close_series = data['Close'].squeeze()
                current_price = float(last_close_series.iloc[-1])
                
                st.metric(label=f"Qiimaha Live-ka ah ee {asset_choice}", value=f"{current_price:.5f}")
                
                bot = UltimateMultiTimeframeBot(symbol=asset_choice, timeframe_choice=tf_choice)
                result = bot.analyze_patterns(data)
                
                if result["Action"] == "BUY":
                    st.success(f"🟢 **{result['Action']} SIGNAL FOUND! ({tf_choice} High Probability)**")
                    st.info(f"**Sababta:** {result['Pattern']}")
                elif result["Action"] == "SELL":
                    st.error(f"🔴 **{result['Action']} SIGNAL FOUND! ({tf_choice} High Probability)**")
                    st.info(f"**Sababta:** {result['Pattern']}")
                elif result["Action"] == "WAIT":
                    st.warning(f"🟡 **BAAJI / WAIT:** {result['Pattern']}")
                else:
                    st.info(f"⚪ **HOLD:** {result['Pattern']}")
            else:
                st.error("Xogta suuqa waa la waayay. Hubi in suuqu furanyahay.")
        except Exception as e:
            st.error(f"Cillad ayaa dhacday: {e}")
