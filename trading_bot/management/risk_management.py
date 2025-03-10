import os
import json
import requests
from trading_bot.core.config import load_config
from trading_bot.api.bitget_api import BitgetAPI
from trading_bot.execution.trade_execution import close_trade

# Load configuration
CONFIG = load_config()
bitget = BitgetAPI(CONFIG["api_key"], CONFIG["api_secret"], CONFIG["api_passphrase"])

TRADE_LOG_FILE = os.path.join(os.getcwd(), "trading_bot", "execution", "trade_log.json")

def calculate_risk(trade):
    """
    Calculate the risk of a given trade.

    :param trade: Trade details
    :return: Risk value
    """
    # Example risk calculation logic
    risk = trade["amount"] * trade["price"] * 0.01  # 1% risk
    return risk

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

def assess_risk():
    """
    Assess the risk of all trades in the trade history.

    :return: List of trades with their risk assessment
    """
    trade_history = get_trade_history()
    risk_assessment = []

    for trade in trade_history:
        risk = calculate_risk(trade)
        trade["risk"] = risk
        risk_assessment.append(trade)

    return risk_assessment

def get_account_balance():
    """
    Fetch account balance from Bitget.
    
    :return: Account balance in USDT
    """
    try:
        balance_data = bitget.get_account_balance()
        if balance_data and "total" in balance_data:
            return float(balance_data["total"])
        return 0.0
    except Exception as e:
        print(f"❌ Error fetching account balance: {e}")
        return 0.0

def check_trade_risk(symbol, entry_price, stop_loss, take_profit):
    """
    Check trade risk based on stop-loss and take-profit levels.

    :param symbol: Trading pair (e.g., "PIUSDT")
    :param entry_price: Entry price of the trade
    :param stop_loss: Stop-loss price level
    :param take_profit: Take-profit price level
    :return: Risk assessment result
    """
    risk_ratio = (entry_price - stop_loss) / (take_profit - entry_price) if take_profit > entry_price else None
    print(f"📊 Risk Ratio for {symbol}: {risk_ratio:.2f}" if risk_ratio else "⚠️ Invalid risk-reward setup!")
    return risk_ratio if risk_ratio else 0.0

def enforce_stop_loss(symbol, current_price):
    """
    Check open trades and close if the price hits stop-loss.

    :param symbol: Trading pair (e.g., "PIUSDT")
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
                if stop_loss and current_price <= stop_loss:
                    print(f"🚨 Stop-loss triggered for {symbol} at {current_price}! Closing trade...")
                    close_trade(trade["order_id"])
                    trade["status"] = "closed"

        with open(TRADE_LOG_FILE, "w") as file:
            json.dump(trades, file, indent=4)

def enforce_take_profit(symbol, current_price):
    """
    Check open trades and close if the price hits take-profit.

    :param symbol: Trading pair (e.g., "PIUSDT")
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
                take_profit = trade.get("take_profit")
                if take_profit and current_price >= take_profit:
                    print(f"✅ Take-profit reached for {symbol} at {current_price}! Closing trade...")
                    close_trade(trade["order_id"])
                    trade["status"] = "closed"

        with open(TRADE_LOG_FILE, "w") as file:
            json.dump(trades, file, indent=4)

# Example Usage
if __name__ == "__main__":
    risk_assessment = assess_risk()
    for trade in risk_assessment:
        print(f"Trade ID: {trade['id']}, Risk: {trade['risk']:.2f}")

    symbol = "PIUSDT"
    entry_price = 1.50
    stop_loss = 1.40
    take_profit = 1.60
    check_trade_risk(symbol, entry_price, stop_loss, take_profit)
