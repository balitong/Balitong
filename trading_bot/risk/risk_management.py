import os
import json
import requests
import time
import logging
from trading_bot.config import API_KEY, API_SECRET, API_PASSPHRASE
from trading_bot.logs.data_logger import log_event
from datetime import datetime
from trading_bot.data.trade_history import get_trade_history
from trading_bot.execution.trade_execution import TradeExecution
from trading_bot.data.market_data import MarketData

# Ensure required libraries are installed
# pip install requests

BITGET_API_URL = "https://api.bitget.com"

# Risk settings (can be modified from GUI)
STOP_LOSS_PERCENT = 3.0  # 3% stop-loss
TAKE_PROFIT_PERCENT = 5.0  # 5% take-profit
DAILY_MAX_LOSS = 500  # Max $500 loss per day

# Risk management settings file
RISK_CONFIG_FILE = "/trading_bot/config/risk_settings.json"

# Default risk management settings
DEFAULT_RISK_SETTINGS = {
    "stop_loss": 5.0,  # Stop-loss percentage
    "take_profit": 10.0,  # Take-profit percentage
    "max_daily_loss": 50.0  # Max daily loss in USDT
}

# Ensure config directory exists
if not os.path.exists("/trading_bot/config"):
    os.makedirs("/trading_bot/config")

def load_risk_settings():
    """Loads risk management settings from file."""
    if not os.path.exists(RISK_CONFIG_FILE):
        save_risk_settings(DEFAULT_RISK_SETTINGS)
    with open(RISK_CONFIG_FILE, "r") as file:
        return json.load(file)

def save_risk_settings(settings):
    """Saves risk management settings to file."""
    with open(RISK_CONFIG_FILE, "w") as file:
        json.dump(settings, file, indent=4)
    log_event("✅ Risk settings updated.")

def check_stop_loss():
    """Checks if stop-loss limit is hit and stops trading."""
    history = get_trade_history()
    total_loss = sum(float(trade["profit/loss"]) for trade in history if float(trade["profit/loss"]) < 0)
    risk_settings = load_risk_settings()

    if abs(total_loss) >= risk_settings["max_daily_loss"]:
        log_event(f"🚨 Max daily loss reached: {total_loss} USDT. Trading halted.")
        return True
    return False

def calculate_position_size(account_balance, risk_percentage, stop_loss_distance):
    """
    Calculate the position size based on account balance, risk percentage, and stop loss distance.

    :param account_balance: Total account balance
    :param risk_percentage: Percentage of account balance to risk
    :param stop_loss_distance: Distance to stop loss in percentage
    :return: Position size
    """
    risk_amount = account_balance * (risk_percentage / 100)
    position_size = risk_amount / stop_loss_distance
    return position_size

def should_execute_trade(account_balance, risk_percentage, stop_loss_distance, current_price, stop_loss_price):
    """
    Determine if a trade should be executed based on risk management rules.

    :param account_balance: Total account balance
    :param risk_percentage: Percentage of account balance to risk
    :param stop_loss_distance: Distance to stop loss in percentage
    :param current_price: Current price of the asset
    :param stop_loss_price: Stop loss price of the asset
    :return: Boolean indicating whether the trade should be executed
    """
    position_size = calculate_position_size(account_balance, risk_percentage, stop_loss_distance)
    potential_loss = (current_price - stop_loss_price) * position_size

    if potential_loss <= account_balance * (risk_percentage / 100):
        return True
    return False

def get_current_balance():
    """Fetches current account balance from Bitget."""
    endpoint = "/api/mix/v1/account/assets"
    url = BITGET_API_URL + endpoint
    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-TIMESTAMP": str(int(time.time())),
        "ACCESS-PASSPHRASE": API_PASSPHRASE
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("balance", 0)
    else:
        log_event(f"⚠️ Failed to fetch balance: {response.text}")
        return 0

def calculate_stop_loss(entry_price):
    """Calculates stop-loss price based on entry price and stop-loss percentage."""
    return entry_price * (1 - STOP_LOSS_PERCENT / 100)

def calculate_risk(order_price, current_price):
    """
    Calculates stop-loss and take-profit levels.
    
    :param order_price: The price at which the order was executed
    :param current_price: The current market price
    :return: Tuple (stop_loss_price, take_profit_price)
    """
    stop_loss_price = order_price * (1 - STOP_LOSS_PERCENT / 100)
    take_profit_price = order_price * (1 + TAKE_PROFIT_PERCENT / 100)
    
    return stop_loss_price, take_profit_price

def check_daily_loss():
    """
    Checks if the total daily loss exceeds the maximum limit.
    :return: Boolean (True if trading should stop)
    """
    history = get_trade_history()
    if not history:
        return False  # No trades, no loss

    today = time.strftime("%Y-%m-%d")
    daily_loss = sum(float(trade["profit/loss"]) for trade in history if trade["timestamp"].startswith(today))

    if daily_loss < -MAX_DAILY_LOSS:
        log_event(f"⚠️ Daily loss limit exceeded! Loss: {daily_loss} USDT. Trading paused.")
        return True

    return False

class RiskManagement:
    """Handles stop-loss, take-profit, and risk control for trades."""

    def __init__(self, max_daily_loss=100, stop_loss_pct=2, take_profit_pct=5):
        """
        Initializes risk management settings.
        :param max_daily_loss: Maximum daily loss allowed (in USDT).
        :param stop_loss_pct: Stop-loss percentage per trade.
        :param take_profit_pct: Take-profit percentage per trade.
        """
        self.trade_execution = TradeExecution()
        self.market_data = MarketData()
        self.max_daily_loss = max_daily_loss
        self.stop_loss_pct = stop_loss_pct / 100
        self.take_profit_pct = take_profit_pct / 100
        self.daily_loss = 0  # Track daily loss

    def check_stop_loss(self, symbol, entry_price):
        """
        Calculates stop-loss price.
        :param symbol: Trading pair (e.g., 'BTC/USDT').
        :param entry_price: Trade entry price.
        :return: Stop-loss price.
        """
        stop_loss_price = entry_price * (1 - self.stop_loss_pct)
        logging.info(f"🛑 Stop-Loss set at: {stop_loss_price} for {symbol}")
        return stop_loss_price

    def check_take_profit(self, symbol, entry_price):
        """
        Calculates take-profit price.
        :param symbol: Trading pair (e.g., 'BTC/USDT').
        :param entry_price: Trade entry price.
        :return: Take-profit price.
        """
        take_profit_price = entry_price * (1 + self.take_profit_pct)
        logging.info(f"✅ Take-Profit set at: {take_profit_price} for {symbol}")
        return take_profit_price

    def monitor_trade(self, symbol, entry_price, order_id):
        """
        Monitors trade for stop-loss and take-profit execution.
        :param symbol: Trading pair (e.g., 'BTC/USDT').
        :param entry_price: Trade entry price.
        :param order_id: Order ID.
        """
        stop_loss_price = self.check_stop_loss(symbol, entry_price)
        take_profit_price = self.check_take_profit(symbol, entry_price)

        while True:
            current_price = self.market_data.get_latest_price(symbol)
            logging.info(f"📊 {symbol} Current Price: {current_price}")

            if current_price <= stop_loss_price:
                logging.warning(f"🛑 Stop-Loss Triggered! Selling {symbol}")
                self.trade_execution.cancel_order(order_id)  # Cancel open order
                self.trade_execution.place_market_order(symbol, "sell", size=0.001)  # Sell at market price
                self.daily_loss += abs(entry_price - current_price)
                break

            if current_price >= take_profit_price:
                logging.info(f"✅ Take-Profit Reached! Selling {symbol}")
                self.trade_execution.cancel_order(order_id)  # Cancel open order
                self.trade_execution.place_market_order(symbol, "sell", size=0.001)  # Sell at market price
                break

    def check_daily_loss(self):
        """
        Checks if the daily loss has exceeded the limit.
        """
        if self.daily_loss >= self.max_daily_loss:
            logging.warning("🚨 Max Daily Loss Limit Reached! Stopping trades.")
            return True
        return False

# Example usage
if __name__ == "__main__":
    save_risk_settings({"stop_loss": 5.0, "take_profit": 15.0, "max_daily_loss": 100.0})
    print(load_risk_settings())

    stop_loss, take_profit = calculate_risk(order_price=3.5, current_price=3.2)
    print(f"🚀 Stop-Loss: {stop_loss}, Take-Profit: {take_profit}")

    if check_daily_loss():
        print("⚠️ Trading stopped due to daily loss limit.")
    else:
        print("✅ Trading within safe limits.")

    risk_manager = RiskManagement(max_risk_per_trade=0.02, max_daily_loss=1000)
    account_balance = 50000
    trade_size = 1500

    if risk_manager.evaluate_risk(account_balance, trade_size):
        logging.info("Trade is within risk limits.")
    else:
        logging.info("Trade exceeds risk limits.")

    risk_manager = RiskManagement(max_daily_loss=100, stop_loss_pct=2, take_profit_pct=5)
    risk_manager.monitor_trade("BTC/USDT", entry_price=60000, order_id="123456789")
