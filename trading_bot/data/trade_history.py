import os
import json
import csv
from datetime import datetime

# Ensure the data directory exists
DATA_DIR = "e:/Signal/trading_bot/data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

TRADE_HISTORY_FILE_JSON = os.path.join(DATA_DIR, "trade_history.json")
TRADE_HISTORY_FILE_CSV = os.path.join(DATA_DIR, "trade_history.csv")

def log_trade_history(trade_data):
    """
    Logs trade execution details to a JSON file.

    :param trade_data: Dictionary containing trade details
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    trade_data["timestamp"] = timestamp

    if os.path.exists(TRADE_HISTORY_FILE_JSON):
        with open(TRADE_HISTORY_FILE_JSON, "r") as file:
            trade_history = json.load(file)
    else:
        trade_history = []

    trade_history.append(trade_data)

    with open(TRADE_HISTORY_FILE_JSON, "w") as file:
        json.dump(trade_history, file, indent=4)

def initialize_trade_history():
    """Creates the trade history file with headers if it doesn't exist."""
    if not os.path.exists(TRADE_HISTORY_FILE_CSV):
        with open(TRADE_HISTORY_FILE_CSV, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "pair", "type", "amount", "price", "profit/loss"])
        print("✅ Trade history initialized.")

def log_trade(pair, trade_type, amount, price, profit_loss):
    """
    Logs a trade into the trade history CSV file.

    :param pair: Trading pair (e.g., "PI/USDT")
    :param trade_type: "BUY" or "SELL"
    :param amount: Amount of asset traded
    :param price: Price at execution
    :param profit_loss: Profit or loss from the trade
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(TRADE_HISTORY_FILE_CSV, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, pair, trade_type, amount, price, profit_loss])

    print(f"📈 Trade Logged: {pair} | {trade_type} | {amount} @ {price} | P/L: {profit_loss}")

def get_trade_history():
    """
    Retrieves all recorded trade history.

    :return: List of trades
    """
    if not os.path.exists(TRADE_HISTORY_FILE_CSV):
        print("⚠️ No trade history found.")
        return []

    with open(TRADE_HISTORY_FILE_CSV, mode="r") as file:
        reader = csv.DictReader(file)
        return list(reader)

# Example usage
if __name__ == "__main__":
    initialize_trade_history()
    log_trade("PI/USDT", "BUY", 50, 3.20, 5.00)
    trade_data = get_trade_history()
    for trade in trade_data:
        print(trade)
