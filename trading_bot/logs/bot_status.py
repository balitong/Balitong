import logging
from datetime import datetime
import os
import time
import json

# Ensure the logs directory exists
LOGS_DIR = os.path.join(os.getcwd(), "trading_bot", "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

STATUS_LOG_FILE = os.path.join(LOGS_DIR, "bot_status.json")

def setup_logger():
    logger = logging.getLogger('bot_status')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('bot_status.log')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def log_status(message):
    logger = setup_logger()
    logger.info(message)

def update_status(status, message=""):
    """
    Updates the bot's status and logs it to a JSON file.

    :param status: Bot status ("RUNNING", "PAUSED", "ERROR", "STOPPED")
    :param message: Additional message or error details
    """
    status_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "message": message
    }

    with open(STATUS_LOG_FILE, "w") as file:
        json.dump(status_data, file, indent=4)

    print(f"📌 Bot Status Updated: {status} - {message}")

def get_status():
    """
    Retrieves the last recorded bot status.

    :return: Dictionary containing the last bot status
    """
    if not os.path.isfile(STATUS_LOG_FILE):
        return {"status": "UNKNOWN", "message": "No status recorded."}

    with open(STATUS_LOG_FILE, "r") as file:
        return json.load(file)

if __name__ == "__main__":
    log_status("Trading bot started.")
    update_status("RUNNING", "Bot started successfully.")
    status = get_status()
    print(f"🔍 Current Status: {status}")
