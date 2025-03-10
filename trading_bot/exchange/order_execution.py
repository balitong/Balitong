import requests
import time
import hmac
import hashlib
import json
import os
from config import API_ENDPOINT, API_KEY, API_SECRET, API_PASS, TRADING_PAIRS, EXCHANGE_API_URL
from config import BITGET_API_URL, TRADING_PAIR, ORDER_TYPE, ORDER_SIZE
from risk_management import check_daily_loss_limit, calculate_risk_levels, record_trade

# Ensure required libraries are installed
# pip install requests

HEADERS = {
    "X-Bitget-APIKEY": API_KEY,
    "X-Bitget-PASSPHRASE": API_PASS,
    "Content-Type": "application/json"
}

# Generate authentication signature
def generate_signature(timestamp, method, request_path, body=""):
    message = f"{timestamp}{method}{request_path}{body}"
    return hmac.new(API_SECRET.encode(), message.encode(), hashlib.sha256).hexdigest()

# Send order to Bitget
def place_order(symbol, side, order_type, price=None, size=1):
    print(f"📌 Placing {order_type} order for {symbol} ({side.upper()})...")

    timestamp = str(int(time.time() * 1000))
    request_path = "/api/mix/v1/order/place-order"

    order_data = {
        "symbol": symbol,
        "side": side,
        "orderType": order_type,
        "size": str(size),
    }

    if order_type == "limit" and price:
        order_data["price"] = str(price)

    body = json.dumps(order_data)
    signature = generate_signature(timestamp, "POST", request_path, body)

    headers = {**HEADERS, "X-Bitget-SIGN": signature, "X-Bitget-TIMESTAMP": timestamp}

    response = requests.post(f"{API_ENDPOINT}{request_path}", headers=headers, data=body)

    if response.status_code == 200:
        print(f"✅ Order executed: {response.json()}")
        return response.json()
    else:
        print(f"❌ Error placing order: {response.text}")
        return None

# Function to execute market or limit order
def place_order(order_type, side, price=None):
    print(f"📌 Placing {order_type.upper()} order: {side.upper()} {TRADING_PAIR}")

    # Check daily loss limit before placing order
    if check_daily_loss_limit(0):
        print("❌ Trading halted due to max daily loss.")
        return None

    order_data = {
        "symbol": TRADING_PAIR,
        "side": side,
        "type": order_type,
        "size": ORDER_SIZE,
        "timestamp": int(time.time() * 1000)
    }

    if order_type == "limit" and price:
        order_data["price"] = price

    headers = {
        "X-BITGET-API-KEY": API_KEY,
        "X-BITGET-SECRET-KEY": API_SECRET,
        "Content-Type": "application/json"
    }

    response = requests.post(f"{BITGET_API_URL}/order", json=order_data, headers=headers)

    if response.status_code == 200:
        order_response = response.json()
        print(f"✅ Order placed successfully: {order_response}")
        return order_response
    else:
        print(f"❌ Order failed: {response.text}")
        return None

# Execute trade with stop-loss and take-profit
def execute_trade():
    entry_price = get_latest_price()
    if not entry_price:
        print("❌ Failed to fetch price data!")
        return

    stop_loss, take_profit = calculate_risk_levels(entry_price)

    # Place market buy order
    buy_order = place_order(ORDER_TYPE, "buy", entry_price)
    if not buy_order:
        return

    time.sleep(3)  # Simulate trade execution

    exit_price = entry_price * 1.01  # Simulate profit scenario
    profit_loss = exit_price - entry_price

    record_trade(TRADING_PAIR, entry_price, exit_price, profit_loss)

    print(f"📊 Trade executed: Entry {entry_price}, Exit {exit_price}")
    print(f"📌 Stop Loss: {stop_loss:.2f}, Take Profit: {take_profit:.2f}")

# Fetch latest price from Bitget API
def get_latest_price():
    response = requests.get(f"{BITGET_API_URL}/ticker/price?symbol={TRADING_PAIR}")
    if response.status_code == 200:
        return float(response.json()["price"])
    else:
        print(f"❌ Failed to fetch latest price: {response.text}")
        return None

# Example execution
if __name__ == "__main__":
    execute_trade()
