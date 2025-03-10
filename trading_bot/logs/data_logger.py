import logging
import os
from datetime import datetime

# Ensure the logs directory exists
LOG_DIR = "e:/Signal/trading_bot/logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure logging
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "trading_bot.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def log_message(message):
    """Log an informational message."""
    logging.info(message)
    print(message)

def log_error(error_message):
    """Log an error message."""
    logging.error(error_message)
    print(f"❌ {error_message}")

def log_event(message, level="info"):
    """
    Logs an event message with a specific severity level.

    :param message: The log message
    :param level: Log level ('info', 'warning', 'error', 'critical')
    """
    levels = {
        "info": logging.info,
        "warning": logging.warning,
        "error": logging.error,
        "critical": logging.critical
    }

    log_func = levels.get(level, logging.info)
    log_func(message)
    print(f"📜 Log: {message}")

def log_trade(trade_data):
    """
    Logs trade execution details.

    :param trade_data: Dictionary containing trade details
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"TRADE | {timestamp} | {trade_data}"
    log_event(log_message, level="info")

# Example usage
if __name__ == "__main__":
    log_message("Trading bot started.")
    log_error("An error occurred.")
    log_event("Trading bot started.", level="info")
    sample_trade = {"pair": "PI/USDT", "type": "BUY", "amount": 100, "price": 3.25}
    log_trade(sample_trade)
    log_event("Trading bot stopped.", level="info")
