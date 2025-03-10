import logging
import os
import time
import traceback
import json

# Ensure the logs directory exists
LOGS_DIR = os.path.join(os.getcwd(), "trading_bot", "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

ERROR_LOG_FILE = os.path.join(LOGS_DIR, "error_log.json")

def setup_logger(name, log_file, level=logging.ERROR):
    """Function to setup a logger"""
    handler = logging.FileHandler(log_file)        
    handler.setLevel(level)

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

def log_error(exception, module_name="Unknown", additional_info=""):
    """
    Logs errors to a JSON file.

    :param exception: Exception instance
    :param module_name: Name of the module where the error occurred
    :param additional_info: Any extra details about the error
    """
    error_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "module": module_name,
        "error_type": type(exception).__name__,
        "error_message": str(exception),
        "traceback": traceback.format_exc(),
        "additional_info": additional_info
    }

    # Append error log to file
    if os.path.isfile(ERROR_LOG_FILE):
        with open(ERROR_LOG_FILE, "r") as file:
            try:
                error_log = json.load(file)
            except json.JSONDecodeError:
                error_log = []
    else:
        error_log = []

    error_log.append(error_data)

    with open(ERROR_LOG_FILE, "w") as file:
        json.dump(error_log, file, indent=4)

    print(f"❌ Error Logged in {module_name}: {str(exception)}")

# Example usage
if __name__ == "__main__":
    try:
        # Simulate an error
        x = 1 / 0
    except Exception as e:
        log_error(e, module_name="test_script", additional_info="Testing error logging.")
