import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from trading_bot.core.config import load_config

# Ensure analytics directory exists
ANALYTICS_DIR = os.path.join(os.getcwd(), "trading_bot", "analytics")
os.makedirs(ANALYTICS_DIR, exist_ok=True)

TRADE_LOG_FILE = os.path.join(ANALYTICS_DIR, "..", "execution", "trade_log.json")

# Load configuration
CONFIG = load_config()

def load_trade_log():
    """
    Load trade log data from JSON file.

    :return: List of trade records
    """
    if not os.path.isfile(TRADE_LOG_FILE):
        print("⚠️ No trade log file found.")
        return []

    with open(TRADE_LOG_FILE, "r") as file:
        try:
            trade_log = json.load(file)
            return trade_log
        except json.JSONDecodeError:
            print("⚠️ Error loading trade log.")
            return []

def analyze_trades():
    """
    Analyze trade log data and print summary statistics.
    """
    trade_log = load_trade_log()
    if not trade_log:
        return

    df = pd.DataFrame(trade_log)
    if df.empty:
        print("⚠️ No trade data available for analysis.")
        return

    print("📊 Trade Analysis Summary:")
    print(df.describe())

    # Example analysis: count trades by status
    status_counts = df['status'].value_counts()
    print("\nTrade Status Counts:")
    print(status_counts)

def load_trade_history():
    """
    Load the trade history from the trade log file.
    
    :return: Pandas DataFrame containing trade data
    """
    if not os.path.isfile(TRADE_LOG_FILE):
        print("⚠️ No trade log found.")
        return pd.DataFrame()

    with open(TRADE_LOG_FILE, "r") as file:
        try:
            trade_data = json.load(file)
            return pd.DataFrame(trade_data)
        except json.JSONDecodeError:
            print("⚠️ Error loading trade log.")
            return pd.DataFrame()

def analyze_trade_performance():
    """
    Analyze past trades for profitability and trends.
    """
    df = load_trade_history()
    if df.empty:
        print("⚠️ No trade data available for analysis.")
        return

    # Convert relevant columns to numeric values
    df["entry_price"] = pd.to_numeric(df["entry_price"], errors="coerce")
    df["exit_price"] = pd.to_numeric(df["exit_price"], errors="coerce")
    df["profit"] = df["exit_price"] - df["entry_price"]

    # Summary statistics
    total_trades = len(df)
    winning_trades = len(df[df["profit"] > 0])
    losing_trades = len(df[df["profit"] < 0])
    win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
    avg_profit = df["profit"].mean()

    print(f"📊 Trade Analysis:")
    print(f"🔹 Total Trades: {total_trades}")
    print(f"✅ Winning Trades: {winning_trades} ({win_rate:.2f}%)")
    print(f"❌ Losing Trades: {losing_trades}")
    print(f"💰 Average Profit Per Trade: {avg_profit:.4f}")

    # Plot profit distribution
    plt.figure(figsize=(10, 5))
    plt.hist(df["profit"], bins=20, color="blue", alpha=0.7)
    plt.axvline(avg_profit, color="red", linestyle="dashed", linewidth=1)
    plt.title("Profit Distribution of Trades")
    plt.xlabel("Profit")
    plt.ylabel("Frequency")
    plt.show()

# Example Usage
if __name__ == "__main__":
    analyze_trade_performance()
