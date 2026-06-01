import pandas as pd
import numpy as np

class ProAnalystBot:
    def __init__(self, symbol, timeframe):
        self.symbol = symbol
        self.timeframe = timeframe  # 15s, 30s, 1m, 2m

    def analyze_patterns(self, df):
        """
        df waa inuu yahay Pandas DataFrame leh oohin: 'open', 'high', 'low', 'close'
        Kani waa algorithm nadiif ah oo ku shaqeeya xeerarkii aad soo baratay.
        """
        if len(df) < 20:  # Waxaan u baahanahay ugu yaraan 20 shumac si aan qaababka waaweyn u xisaabino
            return None

        # Shumacyadii ugu dambeeyey ee suuqa
        c_open = df['open'].iloc[-1]
        c_close = df['close'].iloc[-1]
        c_high = df['high'].iloc[-1]
        c_low = df['low'].iloc[-1]
        
        # Shumacii ka horreeyey (Previous Candle)
        p_open = df['open'].iloc[-2]
        p_close = df['close'].iloc[-2]
        p_high = df['high'].iloc[-2]
        p_low = df['low'].iloc[-2]

        # Xisaabinta guud ee dhererka jirka iyo dabada
        c_body = abs(c_close - c_open)
        c_total_range = c_high - c_low
        p_body = abs(p_close - p_open)

        # ----------------------------------------------------
        # 1. CANDLESTICK PSYCHOLOGY ALGORITHMS
        # ----------------------------------------------------

        # A. Doji Check
        is_doji = c_body <= (c_total_range * 0.1)

        # B. Hammer (Support Zone) & Shooting Star (Resistance Zone)
        # Sifayn: Dabo aad u dheer iyo jir yar oo dhinac u xiga
        c_upper_wick = c_high - max(c_open, c_close)
        c_lower_wick = min(c_open, c_close) - c_low

        is_hammer = (c_lower_wick >= c_body * 2) and (c_upper_wick <= c_body * 0.5)
        is_shooting_star = (c_upper_wick >= c_body * 2) and (c_lower_wick <= c_body * 0.5)

        # C. Engulfing Patterns
        is_bullish_engulfing = (p_close < p_open) and (c_close > c_open) and (c_close >= p_open) and (c_open <= p_close)
        is_bearish_engulfing = (p_close > p_open) and (c_close < c_open) and (c_close <= p_open) and (c_open >= p_close)

        # D. Piercing Line & Dark Cloud Cover (50% Center Rule)
        p_midpoint = p_open + (p_close - p_open) / 2
        
        is_piercing_line = (p_close < p_open) and (c_open < p_close) and (c_close > p_midpoint) and (c_close < p_open)
        is_dark_cloud = (p_close > p_open) and (c_open > p_close) and (c_close < p_midpoint) and (c_close > p_open)

        # E. Tweezer Tops & Bottoms (Identical Wicks Rule)
        # Isku dhibic ama si aad u dhow (0.01% farqi ah)
        is_tweezer_bottom = (p_close < p_open) and (c_close > c_open) and abs(p_low - c_low) <= (c_low * 0.0001)
        is_tweezer_top = (p_close > p_open) and (c_close < c_open) and abs(p_high - c_high) <= (c_high * 0.0001)

        # ----------------------------------------------------
        # 2. CHART PATTERNS ALGORITHMS (M, W, Head & Shoulders)
        # ----------------------------------------------------
        # Waxaan isticmaalaynaa dhibicihii ugu sarreeyey (Peaks) ee 20-kii shumac ee u dambeeyey
        recent_highs = df['high'].tail(20).values
        recent_lows = df['low'].tail(20).values
        
        # Double Top (Xarafka M - Raadinta labo dhibic oo siman)
        is_double_top = abs(max(recent_highs[:10]) - max(recent_highs[10:])) <= (c_close * 0.0005) and (c_close < p_low)
        # Double Bottom (Xarafka W - Raadinta labo sagxadood oo siman)
        is_double_bottom = abs(min(recent_lows[:10]) - min(recent_lows[10:])) <= (c_close * 0.0005) and (c_close > p_high)

        # ----------------------------------------------------
        # 3. SIGNAL GENERATION (OUTPUT)
        # ----------------------------------------------------
        signal = {
            "Asset": self.symbol,
            "Timeframe": self.timeframe,
            "Action": "HOLD",
            "Pattern": "None"
        }

        # Sifee Jihada rasmiga ah ee loo dhufto trade-ka
        if is_hammer or is_bullish_engulfing or is_piercing_line or is_tweezer_bottom or is_double_bottom:
            signal["Action"] = "BUY"
            if is_hammer: signal["Pattern"] = "Hammer Found (Support)"
            elif is_bullish_engulfing: signal["Pattern"] = "Bullish Engulfing"
            elif is_piercing_line: signal["Pattern"] = "Piercing Line (Gap Down + 50%)"
            elif is_tweezer_bottom: signal["Pattern"] = "Tweezer Bottoms"
            elif is_double_bottom: signal["Pattern"] = "Double Bottom (W-Shape Breakout)"

        elif is_shooting_star or is_bearish_engulfing or is_dark_cloud or is_tweezer_top or is_double_top:
            signal["Action"] = "SELL"
            if is_shooting_star: signal["Pattern"] = "Shooting Star Found (Resistance)"
            elif is_bearish_engulfing: signal["Pattern"] = "Bearish Engulfing"
            elif is_dark_cloud: signal["Pattern"] = "Dark Cloud Cover (Gap Up + 50%)"
            elif is_tweezer_top: signal["Pattern"] = "Tweezer Tops"
            elif is_double_top: signal["Pattern"] = "Double Top (M-Shape Breakout)"
            
        elif is_doji:
            signal["Action"] = "WAIT_CONFIRMATION"
            signal["Pattern"] = "Doji (Market Indecision)"

        return signal

# ----------------------------------------------------
# tusaale Sidee Bot-ku u baaraa fursadaha:
# ----------------------------------------------------
# halkan waxaad geli kartaa xogta tooska ah ee Real ama OTC ee laga soo jiado Broker-ka
live_data = {
    'open':  [1.1010, 1.1020, 1.1015, 1.1000],
    'high':  [1.1030, 1.1025, 1.1020, 1.1005],
    'low':   [1.1005, 1.1010, 1.0990, 1.0980],
    'close': [1.1020, 1.1015, 1.1000, 1.1002] # Tusaale shumac ruxmay
}
df_market = pd.DataFrame(live_data)

# tijaabada bot-ka ee lacagta EUR/USD_OTC iyo waqtiga 1-minute
bot = ProAnalystBot(symbol="EUR/USD_OTC", timeframe="1m")
current_signal = bot.analyze_patterns(df_market)
print(current_signal)
