import os
import requests
import json
from trading_bot.core.config import load_config
from trading_bot.api.bitget_api import BitgetAPI
from trading_bot.execution.trade_execution import close_trade

# Load configuration
CONFIG = load_config()
bitget = BitgetAPI(CONFIG["api_key"], CONFIG["api_secret"], CONFIG["api_passphrase"])

TRADE_LOG_FILE = os.path.join(os.getcwd(), "trading_bot", "execution", "trade_log.json")

def send_alert(message):
    """
    Send alert via Telegram or email.

    :param message: Alert message to send
    """
    if CONFIG.get("telegram_bot_token") and CONFIG.get("telegram_chat_id"):
        telegram_url = f"https://api.telegram.org/bot{CONFIG['telegram_bot_token']}/sendMessage"
        payload = {"chat_id": CONFIG["telegram_chat_id"], "text": message}
        try:
            response = requests.post(telegram_url, json=payload)
            if response.status_code == 200:
                print(f"📩 Telegram Alert Sent: {message}")
            else:
                print(f"⚠️ Failed to send Telegram alert: {response.text}")
        except Exception as e:
            print(f"❌ Error sending Telegram alert: {e}")

    if CONFIG.get("email_alerts"):
        print(f"📧 Email alert enabled but not implemented. Message: {message}")

def monitor_price(symbol, current_price):
    """
    Monitor price levels and send alerts for major movements.

    :param symbol: Trading pair (e.g., "PIUSDT")
    :param current_price: Latest price of the asset
    """
    if os.path.exists(TRADE_LOG_FILE):
        with open(TRADE_LOG_FILE, "r") as file:
            try:
                trades = json.load(file)
            except json.JSONDecodeError:
                print("⚠️ Trade log file is corrupted.")
                return

        for trade in trades:
            if trade["symbol"] == symbol and trade["status"] == "open":
                stop_loss = trade.get("stop_loss")
                take_profit = trade.get("take_profit")

                if stop_loss and current_price <= stop_loss:
                    send_alert(f"🚨 Stop-loss triggered for {symbol} at {current_price}. Closing trade...")
                    close_trade(trade["order_id"])
                    trade["status"] = "closed"

                if take_profit and current_price >= take_profit:
                    send_alert(f"✅ Take-profit reached for {symbol} at {current_price}. Closing trade...")
                    close_trade(trade["order_id"])
                    trade["status"] = "closed"

        with open(TRADE_LOG_FILE, "w") as file:
            json.dump(trades, file, indent=4)

def monitor_rsi(symbol, rsi_value):
    """
    Monitor RSI levels and send alerts.

    :param symbol: Trading pair (e.g., "PIUSDT")
    :param rsi_value: Current RSI value
    """
    if rsi_value > 70:
        send_alert(f"⚠️ Overbought Alert: {symbol} RSI is {rsi_value}. Possible reversal.")
    elif rsi_value < 30:
        send_alert(f"⚠️ Oversold Alert: {symbol} RSI is {rsi_value}. Potential buy opportunity.")

# Example Usage
if __name__ == "__main__":
    monitor_price("PIUSDT", 1.45)
    monitor_rsi("PIUSDT", 28)
