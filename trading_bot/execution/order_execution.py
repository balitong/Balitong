import json
import requests
import os
import time
from dotenv import load_dotenv
from trading_bot.logs.data_logger import log_event, log_trade
from trading_bot.config import API_KEY, API_SECRET, API_PASSPHRASE, BITGET_BASE_URL

# Ensure required libraries are installed
# pip install requests python-dotenv

# Load environment variables
load_dotenv()

# Bitget API Endpoints
PLACE_ORDER_URL = f"{BITGET_BASE_URL}/api/v1/orders"

def execute_order(pair, order_type, amount, price=None):
    """
    Executes a market or limit order on Bitget.

    :param pair: Trading pair (e.g., "PI/USDT")
    :param order_type: "BUY" or "SELL"
    :param amount: Amount of asset to trade
    :param price: Price for limit orders (None for market orders)
    :return: API response as JSON
    """
    headers = {
        "Content-Type": "application/json",
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": API_SECRET,
        "ACCESS-PASSPHRASE": API_PASSPHRASE
    }

    order_data = {
        "symbol": pair.replace("/", ""),
        "side": order_type.lower(),
        "size": str(amount),
        "type": "limit" if price else "market",
        "price": str(price) if price else None
    }

    try:
        response = requests.post(PLACE_ORDER_URL, headers=headers, data=json.dumps(order_data))
        result = response.json()

        if result.get("code") == "00000":
            log_trade({"pair": pair, "type": order_type, "amount": amount, "price": price or "Market"})
            log_event(f"✅ Order executed: {order_data}")
            return result
        else:
            log_event(f"⚠️ Order failed: {result.get('msg')}", level="error")
            return None
    except Exception as e:
        log_event(f"❌ API Error: {str(e)}", level="error")
        return None

# Example usage
if __name__ == "__main__":
    response = execute_order("PI/USDT", "BUY", 10, 3.25)
    print(response)
