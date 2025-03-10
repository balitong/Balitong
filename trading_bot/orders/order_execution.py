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
BITGET_API_URL = "https://api.bitget.com"

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

def send_order(symbol, side, quantity, order_type="market", price=None):
    """
    Executes an order on Bitget.
    
    :param symbol: Trading pair (e.g., "PIUSDT")
    :param side: "BUY" or "SELL"
    :param quantity: Amount to trade
    :param order_type: "market" or "limit"
    :param price: Required for limit orders
    :return: API response
    """
    endpoint = "/api/mix/v1/order/place"
    url = BITGET_API_URL + endpoint
    
    payload = {
        "symbol": symbol,
        "side": side.lower(),
        "size": quantity,
        "orderType": order_type.lower(),
        "timeInForce": "GTC"
    }

    if order_type.lower() == "limit":
        if price is None:
            log_event("⚠️ Limit order requires a price!")
            return None
        payload["price"] = price

    headers = {
        "Content-Type": "application/json",
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": generate_signature(payload),
        "ACCESS-TIMESTAMP": str(int(time.time())),
        "ACCESS-PASSPHRASE": API_PASSPHRASE
    }

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        log_event(f"✅ Order executed successfully: {response.json()}")
        return response.json()
    else:
        log_event(f"❌ Order execution failed: {response.text}")
        return None

def generate_signature(payload):
    """Generates API signature for Bitget authentication."""
    import hmac
    import hashlib
    import base64

    message = json.dumps(payload)
    secret_bytes = bytes(API_SECRET, "utf-8")
    message_bytes = bytes(message, "utf-8")

    signature = hmac.new(secret_bytes, message_bytes, digestmod=hashlib.sha256).digest()
    return base64.b64encode(signature).decode()

# Example usage
if __name__ == "__main__":
    response = execute_order("PI/USDT", "BUY", 10, 3.25)
    print(response)
