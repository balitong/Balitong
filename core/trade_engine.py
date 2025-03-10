import os
import sys
import time
import logging
from datetime import datetime

# Ensure the module can find other core components
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.order_manager import OrderManager
from core.data_feed import DataFeed
from core.strategy import TradingStrategy

# Logging setup
LOG_FILE = os.path.join(os.path.dirname(__file__), "../logs/trade_engine.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class TradeEngine:
    def __init__(self):
        # Initialize the trade engine
        pass

    def start(self):
        # Start the trade engine
        pass

    def stop(self):
        # Stop the trade engine
        pass

    def execute_trade(self, trade):
        # Execute a trade
        pass

class TradingBot:
    def __init__(self, debug=False, source=None):  # Check what arguments it accepts
        """
        Initialize the trading bot.
        :param debug: If True, enables debug mode for detailed logging.
        :param source: The data source for the data feed.
        """
        self.debug = debug
        self.data_feed = DataFeed(source)  # Remove source argument
        self.order_manager = OrderManager()
        self.strategy = TradingStrategy()
        self.running = False

        if self.debug:
            print("TradingBot initialized in DEBUG mode.")

    def run(self):
        """
        Main loop to execute trading logic.
        """
        self.running = True
        logging.info("Trading bot started.")

        while self.running:
            try:
                # Fetch latest market data
                market_data = self.data_feed.get_latest_data()
                if self.debug:
                    print(f"Market Data: {market_data}")

                # Analyze data and determine trading signals
                trade_signal = self.strategy.analyze_market(market_data)
                if self.debug:
                    print(f"Trade Signal: {trade_signal}")

                # Execute trade if conditions are met
                if trade_signal:
                    order_response = self.order_manager.execute_order(trade_signal)
                    logging.info(f"Trade Executed: {order_response}")
                    if self.debug:
                        print(f"Order Response: {order_response}")

                # Sleep to prevent overloading the API
                time.sleep(5)

            except Exception as e:
                logging.error(f"Error in trading loop: {str(e)}")
                if self.debug:
                    print(f"Error: {e}")

    def stop(self):
        """
        Stops the trading bot safely.
        """
        self.running = False
        logging.info("Trading bot stopped.")
        if self.debug:
            print("Trading bot has been stopped.")

if __name__ == "__main__":
    bot = TradingBot(debug=True)  # Keep only the expected arguments
    bot.run()
