import os
import json
from datetime import datetime
from trading_bot.logs.data_logger import log_event
from trading_bot.data.trade_history import get_trade_history

# Ensure required libraries are installed
# pip install 

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
