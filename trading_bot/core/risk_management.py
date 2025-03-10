import os
import json
import time
import pandas as pd
from config import RISK_CONFIG_PATH, MAX_DAILY_LOSS, TAKE_PROFIT_PERCENT, STOP_LOSS_PERCENT
from trading_bot.core.config import load_config

# Ensure required libraries are installed
# pip install

# Load configuration settings
CONFIG = load_config()

# Ensure the risk management directory exists
RISK_MANAGEMENT_DIR = os.path.join(os.getcwd(), "trading_bot", "core")
os.makedirs(RISK_MANAGEMENT_DIR, exist_ok=True)

TRADE_LOG_FILE = os.path.join(RISK_MANAGEMENT_DIR, "..", "execution", "trade_log.json")

# Load or initialize risk settings
def load_risk_settings():
    if os.path.exists(RISK_CONFIG_PATH):
        with open(RISK_CONFIG_PATH, "r") as file:
            return json.load(file)
    else:
        return {"daily_loss": 0, "trades": []}

# Save risk settings
def save_risk_settings(data):
    with open(RISK_CONFIG_PATH, "w") as file:
        json.dump(data, file, indent=4)

# Check if the daily loss limit is reached
def check_daily_loss_limit(current_loss):
    risk_data = load_risk_settings()
    
    risk_data["daily_loss"] += current_loss
    save_risk_settings(risk_data)

    if risk_data["daily_loss"] >= MAX_DAILY_LOSS:
        print("❌ Max daily loss limit reached! Trading halted for today.")
        return True
    return False

# Calculate stop-loss and take-profit levels
def calculate_risk_levels(entry_price):
    stop_loss = entry_price * (1 - STOP_LOSS_PERCENT / 100)
    take_profit = entry_price * (1 + TAKE_PROFIT_PERCENT / 100)
    return stop_loss, take_profit

# Record trade results
def record_trade(symbol, entry_price, exit_price, profit_loss):
    risk_data = load_risk_settings()
    
    trade = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "profit_loss": profit_loss
    }

    risk_data["trades"].append(trade)
    save_risk_settings(risk_data)

    print(f"📊 Trade recorded: {trade}")

def load_trade_data():
    """
    Load trade history for risk analysis.
    
    :return: Pandas DataFrame containing trade data
    """
    if not os.path.isfile(TRADE_LOG_FILE):
        print("⚠️ No trade log found.")
        return pd.DataFrame()

    with open(TRADE_LOG_FILE, "r") as file:
        try:
            trade_data = json.load(file)
            return pd.DataFrame(trade_data)
        except json.JSONDecodeError:
            print("⚠️ Error loading trade log.")
            return pd.DataFrame()

def set_stop_loss(entry_price, stop_loss_pct):
    """
    Calculate stop-loss price.
    
    :param entry_price: The price at which the trade was entered
    :param stop_loss_pct: Stop-loss percentage
    :return: Calculated stop-loss price
    """
    stop_loss_price = entry_price * (1 - stop_loss_pct / 100)
    return round(stop_loss_price, 4)

def set_take_profit(entry_price, take_profit_pct):
    """
    Calculate take-profit price.
    
    :param entry_price: The price at which the trade was entered
    :param take_profit_pct: Take-profit percentage
    :return: Calculated take-profit price
    """
    take_profit_price = entry_price * (1 + take_profit_pct / 100)
    return round(take_profit_price, 4)

def monitor_trade_risk():
    """
    Analyze trade risks and check if stop-loss or take-profit was hit.
    """
    df = load_trade_data()
    if df.empty:
        print("⚠️ No trade data available for risk monitoring.")
        return

    # Convert relevant columns to numeric values
    df["entry_price"] = pd.to_numeric(df["entry_price"], errors="coerce")
    df["exit_price"] = pd.to_numeric(df["exit_price"], errors="coerce")
    df["profit"] = df["exit_price"] - df["entry_price"]

    # Risk assessment
    max_drawdown = df["profit"].min()
    max_profit = df["profit"].max()

    print(f"📊 Risk Assessment:")
    print(f"🔹 Maximum Drawdown: {max_drawdown:.4f}")
    print(f"🔹 Maximum Profit: {max_profit:.4f}")

    # Risk recommendations
    if max_drawdown < -CONFIG["max_risk_per_trade"]:
        print("⚠️ High Risk Detected: Consider adjusting stop-loss levels.")

# Example usage
if __name__ == "__main__":
    # Simulate a trade
    symbol = "BTC/USDT"
    entry_price = 50000
    exit_price = 50500
    profit_loss = exit_price - entry_price

    if not check_daily_loss_limit(profit_loss):
        record_trade(symbol, entry_price, exit_price, profit_loss)
        stop_loss, take_profit = calculate_risk_levels(entry_price)
        print(f"📌 Stop Loss: {stop_loss:.2f}, Take Profit: {take_profit:.2f}")

    entry = 100  # Example entry price
    stop_loss = set_stop_loss(entry, CONFIG["stop_loss_pct"])
    take_profit = set_take_profit(entry, CONFIG["take_profit_pct"])
    
    print(f"📉 Stop-Loss Price: {stop_loss}")
    print(f"📈 Take-Profit Price: {take_profit}")
    
    monitor_trade_risk()

def calculate_risk(account_balance, trade_size, risk_percentage):
    """
    Calculate the risk for a given trade.
    
    Parameters:
    - account_balance: The total account balance.
    - trade_size: The size of the trade.
    - risk_percentage: The percentage of the account balance to risk.
    
    Returns:
    - risk_amount: The amount of money at risk.
    """
    risk_amount = (account_balance * risk_percentage) / 100
    if trade_size > risk_amount:
        print("⚠️ Warning: Trade size exceeds the risk limit!")
        return risk_amount
    return trade_size

class RiskManagement:
    def __init__(self, max_risk_per_trade: float, max_risk_per_day: float):
        self.max_risk_per_trade = max_risk_per_trade
        self.max_risk_per_day = max_risk_per_day
        self.current_risk = 0

    def set_max_risk_per_trade(self, max_risk_per_trade: float):
        self.max_risk_per_trade = max_risk_per_trade

    def get_max_risk_per_trade(self) -> float:
        return self.max_risk_per_trade

    def set_max_risk_per_day(self, max_risk_per_day: float):
        self.max_risk_per_day = max_risk_per_day

    def get_max_risk_per_day(self) -> float:
        return self.max_risk_per_day

    def calculate_risk(self, trade_amount: float) -> float:
        risk = trade_amount * self.max_risk_per_trade
        if risk + self.current_risk > self.max_risk_per_day:
            raise ValueError("Risk exceeds the maximum allowed risk for the day")
        self.current_risk += risk
        return risk

    def calculate_position_size(self, stop_loss_amount):
        """
        Calculate the position size based on the stop loss amount.

        :param stop_loss_amount: Amount of money willing to risk on a trade
        :return: Position size
        """
        risk_amount = self.account_balance * (self.max_risk_per_trade / 100)
        position_size = risk_amount / stop_loss_amount
        return position_size

# Example usage
if __name__ == "__main__":
    risk_manager = RiskManagement(max_risk_per_trade=1, account_balance=10000)
    position_size = risk_manager.calculate_position_size(stop_loss_amount=50)
    print(f"Calculated position size: {position_size}")