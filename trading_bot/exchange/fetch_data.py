import requests
import pandas as pd
import time
import os
from config import API_ENDPOINT, API_KEY, API_SECRET, TRADING_PAIRS, RAW_DATA_PATH

# Ensure required libraries are installed
# pip install requests pandas

HEADERS = {
    "X-Bitget-APIKEY": API_KEY,
    "Content-Type": "application/json"
}

# Function to fetch historical market data from Bitget
def fetch_market_data(symbol, interval="1m", limit=500):
    print(f"📥 Fetching market data for {symbol}...")

    url = f"{API_ENDPOINT}/api/mix/v1/market/candles?symbol={symbol}&granularity={interval}&limit={limit}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()["data"]
        df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df.sort_values("timestamp")  # Ensure data is sorted

        # Save data to CSV
        file_path = f"{RAW_DATA_PATH}{symbol}_data.csv"
        df.to_csv(file_path, index=False)
        print(f"✅ Data saved: {file_path}")

        return df
    else:
        print(f"❌ Error fetching data for {symbol}: {response.text}")
        return None

# Fetch data for all trading pairs
if __name__ == "__main__":
    for pair in TRADING_PAIRS:
        fetch_market_data(pair)
        time.sleep(1)  # Avoid API rate limits

    print("✅ Market data collection complete!")
