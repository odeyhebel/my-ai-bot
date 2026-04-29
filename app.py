import pandas as pd
import numpy as np
import time

# 1. Liiska Pairs-ka (7 Real & 10 OTC)
REAL_MARKET_PAIRS = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'EUR/GBP', 'USD/CAD', 'NZD/USD']
OTC_MARKET_PAIRS = ['EUR/USD-OTC', 'GBP/USD-OTC', 'USD/JPY-OTC', 'AUD/USD-OTC', 'EUR/GBP-OTC', 
                    'USD/CHF-OTC', 'NZD/USD-OTC', 'USD/CAD-OTC', 'EUR/JPY-OTC', 'GBP/JPY-OTC']

# 2. Waqtiyada Ganacsiga (Expiraion Times)
TIME_FRAMES = ['5s', '15s', '30s', '1m', '2m', '3m', '5m']

def analyze_strategy(df):
    """
    Logic-ga falanqaynta (RSI, MA, Stochastic)
    """
    # Moving Averages
    df['ma_fast'] = df['close'].rolling(window=7).mean()
    df['ma_mid'] = df['close'].rolling(window=14).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['rsi'] = 100 - (100 / (1 + (gain/loss)))

    # Stochastic
    low_min = df['low'].rolling(window=14).min()
    high_max = df['high'].rolling(window=14).max()
    df['k_line'] = 100 * ((df['close'] - low_min) / (high_max - low_min))
    df['d_line'] = df['k_line'].rolling(window=3).mean()

    last = df.iloc[-1]
    
    # Logic: BUY
    if last['ma_fast'] > last['ma_mid'] and last['rsi'] < 40 and last['k_line'] > last['d_line']:
        return "BUY"
    # Logic: SELL
    elif last['ma_fast'] < last['ma_mid'] and last['rsi'] > 60 and last['k_line'] < last['d_line']:
        return "SELL"
    
    return "WAIT"

# --- LOOP-KA SHAQADA ---
print(f"Bot-ku wuxuu bilaabayaa falanqaynta {len(REAL_MARKET_PAIRS)} Real Pairs iyo {len(OTC_MARKET_PAIRS)} OTC Pairs...")

# Tusaale ahaan sida uu u dhex wareegayo pairs-ka
for pair in REAL_MARKET_PAIRS + OTC_MARKET_PAIRS:
    for tf in TIME_FRAMES:
        print(f"Checking {pair} on {tf} timeframe...")
        # Halkan bot-ku wuxuu ka akhrin lahaa xogta live-ka ah (API call)
        time.sleep(0.1) 
