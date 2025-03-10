import pandas as pd
import os
import csv
import datetime
import logging

TRADE_HISTORY_FILE = "data/trade_history.csv"

class TradeData:
    """Handles trade history and performance tracking."""

    def __init__(self, file_path: str = TRADE_HISTORY_FILE):
        self.file_path = file_path
        self.data = None
        self.ensure_file_exists()

    def ensure_file_exists(self):
        """Creates trade history file if it does not exist."""
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["timestamp", "pair", "side", "entry_price", "exit_price", "profit_loss"])
            logging.info("✅ Trade history file created.")

    def log_trade(self, pair, side, entry_price, exit_price):
        """
        Logs a completed trade to the trade history file.
        :param pair: Trading pair (e.g., "BTC/USDT")
        :param side: "buy" or "sell"
        :param entry_price: Price at which trade was entered
        :param exit_price: Price at which trade was exited
        """
        profit_loss = round(exit_price - entry_price, 2)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.file_path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, pair, side, entry_price, exit_price, profit_loss])

        logging.info(f"📊 Trade logged: {pair} {side} | Entry: {entry_price}, Exit: {exit_price}, P/L: {profit_loss}")

    def get_daily_loss(self):
        """Calculates the total daily loss from trade history."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        total_loss = 0

        with open(self.file_path, "r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header

            for row in reader:
                if row and row[0].startswith(today):
                    profit_loss = float(row[-1])
                    if profit_loss < 0:
                        total_loss += abs(profit_loss)

        logging.info(f"📉 Daily loss calculated: {total_loss}")
        return total_loss

    def load_data(self):
        """Load trade data from a CSV file."""
        self.data = pd.read_csv(self.file_path)
        return self.data

    def process_data(self):
        """Process the trade data."""
        if self.data is not None:
            # ...existing code...
            # Add your data processing logic here
            # ...existing code...
            pass
        else:
            raise ValueError("Data not loaded. Please load the data first.")

    def save_data(self, output_path: str):
        """Save the processed data to a CSV file."""
        if self.data is not None:
            self.data.to_csv(output_path, index=False)
        else:
            raise ValueError("Data not loaded. Please load the data first.")
