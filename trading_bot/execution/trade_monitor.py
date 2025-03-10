import logging
import os
import json
import time
import requests
from trading_bot.core.config import load_config

class TradeMonitor:
    def __init__(self):
        self.is_monitoring = False
        self.logger = logging.getLogger('TradeMonitor')
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def start_monitoring(self):
        self.is_monitoring = True
        self.logger.info("Trade monitoring started.")
        # ...existing code...

    def stop_monitoring(self):
        self.is_monitoring = False
        self.logger.info("Trade monitoring stopped.")
        # ...existing code...

    def log_trade_activity(self, trade_info):
        if self.is_monitoring:
            self.logger.info(f"Trade activity: {trade_info}")
        # ...existing code...

# Ensure execution directory exists
EXECUTION_DIR = os.path.join(os.getcwd(), "trading_bot", "execution")
os.makedirs(EXECUTION_DIR, exist_ok=True)

TRADE_LOG_FILE = os.path.join(EXECUTION_DIR, "trade_log.json")

# Load API settings
CONFIG = load_config()
API_KEY = CONFIG["bitget"]["api_key"]
API_SECRET = CONFIG["bitget"]["api_secret"]
BASE_URL = "https://api.bitget.com"

HEADERS = {
    "Content-Type": "application/json",
    "ACCESS-KEY": API_KEY,
}

def get_trade_status(order_id):
    """
    Retrieve trade execution status from Bitget.

    :param order_id: ID of the executed trade
    :return: API response
    """
    url = f"{BASE_URL}/api/v1/orders/status?orderId={order_id}"

    try:
        response = requests.get(url, headers=HEADERS)
        data = response.json()
        return data
    except Exception as e:
        print(f"❌ Error fetching trade status: {e}")
        return None

def update_trade_log():
    """
    Update trade logs with latest trade execution status.
    """
    if not os.path.isfile(TRADE_LOG_FILE):
        print("⚠️ No trade log file found.")
        return

    with open(TRADE_LOG_FILE, "r") as file:
        try:
            trade_log = json.load(file)
        except json.JSONDecodeError:
            print("⚠️ Error loading trade log.")
            return

    for trade in trade_log:
        if "orderId" in trade and "status" not in trade:
            status = get_trade_status(trade["orderId"])
            if status and "status" in status:
                trade["status"] = status["status"]

    with open(TRADE_LOG_FILE, "w") as file:
        json.dump(trade_log, file, indent=4)

    print("✅ Trade log updated.")

def monitor_trades(interval=10):
    """
    Monitor open trades and update their status.

    :param interval: Time (seconds) between checks
    """
    while True:
        print("🔄 Checking open trades...")
        update_trade_log()
        time.sleep(interval)

# Example Usage
if __name__ == "__main__":
    monitor_trades(interval=30)
