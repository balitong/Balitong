import os
import time
import json
import requests
from trading_bot.core.config import load_config
from trading_bot.api.bitget_api import BitgetAPI
from trading_bot.execution.trade_execution import log_trade

class TradeMonitoring:
    def __init__(self):
        self.is_monitoring = False

    def start_monitoring(self):
        self.is_monitoring = True
        print("Trade monitoring started.")

    def stop_monitoring(self):
        self.is_monitoring = False
        print("Trade monitoring stopped.")

    def monitor_trades(self):
        if not self.is_monitoring:
            print("Monitoring is not active.")
            return
        # Logic to monitor trades goes here

# Load configuration
CONFIG = load_config()
bitget = BitgetAPI(CONFIG["api_key"], CONFIG["api_secret"], CONFIG["api_passphrase"])

TRADE_LOG_FILE = os.path.join(os.getcwd(), "trading_bot", "execution", "trade_log.json")

def get_open_orders(symbol):
    """
    Fetch open orders from Bitget.

    :param symbol: Trading pair (e.g., "PIUSDT")
    :return: List of open orders
    """
    try:
        response = bitget.get_open_orders(symbol)
        if response:
            print(f"📊 Open Orders for {symbol}: {response}")
        return response
    except Exception as e:
        print(f"❌ Error fetching open orders: {e}")
        return None

def get_trade_history():
    """
    Retrieve trade history from the log file.

    :return: List of trade history records
    """
    if os.path.exists(TRADE_LOG_FILE):
        with open(TRADE_LOG_FILE, "r") as file:
            try:
                trade_history = json.load(file)
                return trade_history
            except json.JSONDecodeError:
                print("⚠️ Trade log file is corrupted.")
                return []
    return []

def monitor_trade(symbol):
    """
    Monitor trade status and detect major price movements.

    :param symbol: Trading pair (e.g., "PIUSDT")
    """
    print(f"🚀 Monitoring {symbol} for price movements...")

    previous_price = None

    while True:
        try:
            ticker = bitget.get_ticker(symbol)
            if ticker and "last" in ticker:
                current_price = float(ticker["last"])

                if previous_price is not None:
                    price_change = (current_price - previous_price) / previous_price * 100

                    if abs(price_change) > CONFIG["alert_threshold"]:
                        print(f"⚠️ Major Price Movement Detected! {symbol} changed by {price_change:.2f}%")

                previous_price = current_price
            else:
                print(f"⚠️ Failed to fetch price for {symbol}")

            time.sleep(CONFIG["monitoring_interval"])

        except KeyboardInterrupt:
            print("🛑 Stopping trade monitoring...")
            break
        except Exception as e:
            print(f"❌ Error monitoring trade: {e}")

# Example Usage
if __name__ == "__main__":
    # Example monitoring
    monitor_trade("PIUSDT")
