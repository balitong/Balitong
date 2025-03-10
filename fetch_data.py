import requests
import pandas as pd
import time
import os
from config import TRADING_PAIRS, RAW_DATA_PATH

# Ensure required libraries are installed
# pip install requests pandas

# Bitget API endpoint for historical data
BITGET_API_URL = "https://api.bitget.com/api/v2/market/candles"

# Timeframe for historical data
TIMEFRAME = "15m"  # Options: 5m, 15m, 1h, 4h
LIMIT = 500  # Number of candles per request

def fetch_candles(symbol):
    """Fetch historical candlestick data from Bitget."""
    params = {
        "symbol": symbol.upper().replace("_", ""),  # Bitget format (PIUSDT, BTCUSDT)
        "granularity": TIMEFRAME,
        "limit": LIMIT,
    }
    try:
        response = requests.get(BITGET_API_URL, params=params)
        data = response.json()
        
        if "data" in data:
            return data["data"]
        else:
            print(f"⚠️ Error fetching {symbol}: {data}")
            return None
    except Exception as e:
        print(f"❌ API request failed for {symbol}: {e}")
        return None

def save_data(symbol):
    """Download & save data to CSV."""
    print(f"📊 Fetching data for {symbol}...")
    data = bot.data_feed.get_data()  # Use correct method name
    
    if data:
        df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        
        # Ensure directory exists
        os.makedirs(RAW_DATA_PATH, exist_ok=True)
        
        # Save to CSV
        file_path = f"{RAW_DATA_PATH}{symbol}.csv"
        df.to_csv(file_path, index=False)
        print(f"✅ Saved {symbol} data -> {file_path}")

# Fetch data for all trading pairs
for pair in TRADING_PAIRS:
    save_data(pair)

print("✅ Data fetching complete!")
