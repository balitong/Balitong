import os
import json
import time
import requests
from trading_bot.core.config import load_config
from trading_bot.core.risk_management import calculate_stop_loss, calculate_take_profit

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

def log_trade(trade_data):
    """
    Log executed trades into a JSON file.

    :param trade_data: Dictionary containing trade details
    """
    if os.path.isfile(TRADE_LOG_FILE):
        with open(TRADE_LOG_FILE, "r") as file:
            try:
                trade_log = json.load(file)
            except json.JSONDecodeError:
                trade_log = []
    else:
        trade_log = []

    trade_log.append(trade_data)

    with open(TRADE_LOG_FILE, "w") as file:
        json.dump(trade_log, file, indent=4)

def place_market_order(symbol, side, quantity):
    """
    Execute a market order on Bitget.

    :param symbol: Trading pair (e.g., "PIUSDT")
    :param side: "buy" or "sell"
    :param quantity: Amount to trade
    :return: API response
    """
    url = f"{BASE_URL}/api/v1/orders/market"
    payload = {
        "symbol": symbol,
        "side": side,
        "size": quantity,
    }

    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        data = response.json()
        if "orderId" in data:
            print(f"✅ Market Order Executed: {symbol} {side.upper()} {quantity}")
            log_trade(data)
        else:
            print(f"❌ Market Order Failed: {data}")
        return data
    except Exception as e:
        print(f"❌ Error placing market order: {e}")
        return None

def place_limit_order(symbol, side, quantity, price):
    """
    Execute a limit order on Bitget.

    :param symbol: Trading pair (e.g., "PIUSDT")
    :param side: "buy" or "sell"
    :param quantity: Amount to trade
    :param price: Limit price
    :return: API response
    """
    url = f"{BASE_URL}/api/v1/orders/limit"
    payload = {
        "symbol": symbol,
        "side": side,
        "size": quantity,
        "price": price,
    }

    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        data = response.json()
        if "orderId" in data:
            print(f"✅ Limit Order Placed: {symbol} {side.upper()} {quantity} @ {price}")
            log_trade(data)
        else:
            print(f"❌ Limit Order Failed: {data}")
        return data
    except Exception as e:
        print(f"❌ Error placing limit order: {e}")
        return None

class TradeExecution:
    def __init__(self, broker_api):
        """
        Initialize the TradeExecution class.

        :param broker_api: An instance of the broker API
        """
        self.broker_api = broker_api

    def execute_trade(self, symbol, quantity, trade_type):
        """
        Execute a trade.

        :param symbol: The trading pair symbol (e.g., "BTC/USDT")
        :param quantity: The quantity to trade
        :param trade_type: The type of trade ("buy" or "sell")
        :return: Trade execution result
        """
        if trade_type not in ["buy", "sell"]:
            raise ValueError("Invalid trade type. Must be 'buy' or 'sell'.")

        order = self.broker_api.create_order(symbol, quantity, trade_type)
        print(f"🔄 Executing {trade_type} order for {quantity} {symbol}...")
        time.sleep(2)  # Simulate network delay
        print(f"✅ Trade executed: {order}")
        return order

# Example usage
if __name__ == "__main__":
    class MockBrokerAPI:
        def create_order(self, symbol, quantity, trade_type):
            return {
                "symbol": symbol,
                "quantity": quantity,
                "trade_type": trade_type,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

    broker_api = MockBrokerAPI()
    trade_executor = TradeExecution(broker_api)
    trade_executor.execute_trade("BTC/USDT", 0.1, "buy")

    symbol = "PIUSDT"
    entry_price = 100.0  # Simulated price
    quantity = 1

    stop_loss = calculate_stop_loss(entry_price)
    take_profit = calculate_take_profit(entry_price)

    # Place Market Order
    place_market_order(symbol, "buy", quantity)

    # Place Limit Order
    place_limit_order(symbol, "buy", quantity, stop_loss)
