import os
import pickle
import numpy as np
import pandas as pd
import ta  # Technical Analysis library
import requests
from datetime import datetime
from trading_bot.logs.data_logger import log_event
from trading_bot.data.market_data import get_latest_market_data

# Ensure required libraries are installed
# pip install numpy pandas ta requests

SIGNAL_API_URL = "https://api.example.com/trading_signals"

# AI Model Storage Path
MODEL_FILE = "/trading_bot/ai/models/trade_prediction_model.pkl"

# Ensure model exists
if not os.path.exists(MODEL_FILE):
    log_event("⚠️ AI Model not found. Train it first using ai_trade_analysis.py.")
    MODEL_FILE = None

def load_ai_model():
    """Loads trained AI model from file."""
    if not MODEL_FILE:
        return None
    with open(MODEL_FILE, "rb") as file:
        return pickle.load(file)

def generate_technical_signals(data):
    """Generates buy/sell signals based on technical indicators."""
    data["rsi"] = ta.momentum.RSIIndicator(data["close"]).rsi()
    data["macd"] = ta.trend.MACD(data["close"]).macd()
    data["sma_50"] = ta.trend.SMAIndicator(data["close"], window=50).sma_indicator()
    data["sma_200"] = ta.trend.SMAIndicator(data["close"], window=200).sma_indicator()

    data["buy_signal"] = (data["rsi"] < 30) & (data["macd"] > 0) & (data["sma_50"] > data["sma_200"])
    data["sell_signal"] = (data["rsi"] > 70) & (data["macd"] < 0) & (data["sma_50"] < data["sma_200"])

    return data

def generate_ai_signal(data):
    """Uses AI model to predict trade direction."""
    model = load_ai_model()
    if not model:
        return None

    features = data.drop(columns=["close", "timestamp"])
    prediction = model.predict(features)
    return prediction

def get_trading_signal():
    """Generates final trading signal combining AI & technical analysis."""
    data = get_latest_market_data()
    data = generate_technical_signals(data)

    ai_signal = generate_ai_signal(data) if MODEL_FILE else None

    if data.iloc[-1]["buy_signal"]:
        return "BUY"
    elif data.iloc[-1]["sell_signal"]:
        return "SELL"
    elif ai_signal is not None:
        return "BUY" if ai_signal[-1] == 1 else "SELL"
    else:
        return "HOLD"

def fetch_trading_signals():
    """
    Fetch trading signals from an external API.

    :return: DataFrame containing trading signals
    """
    response = requests.get(SIGNAL_API_URL)
    if response.status_code == 200:
        signals = response.json()
        return pd.DataFrame(signals)
    else:
        print(f"Failed to fetch trading signals: {response.status_code}")
        return pd.DataFrame()

def process_signals(df):
    """
    Process trading signals for further analysis.

    :param df: DataFrame containing trading signals
    :return: Processed DataFrame
    """
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    return df

def generate_signals_report(df):
    """
    Generate a report from trading signals.

    :param df: DataFrame containing trading signals
    :return: None
    """
    report = df.describe()
    print("Trading Signals Report:")
    print(report)

# Example usage
if __name__ == "__main__":
    signals_df = fetch_trading_signals()
    if not signals_df.empty:
        processed_signals = process_signals(signals_df)
        generate_signals_report(processed_signals)
