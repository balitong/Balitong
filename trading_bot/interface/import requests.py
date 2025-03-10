import requests
import time
import logging
from trading_bot.config.config import API_KEY, API_SECRET, API_PASSPHRASE
from trading_bot.api.bitget_api import BitgetAPI

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class TradeExecution:
    """Handles trade execution logic for market and limit orders."""

    def __init__(self):
        self.api = BitgetAPI(API_KEY, API_SECRET, API_PASSPHRASE)

    def place_market_order(self, symbol, side, size):
        """
        Places a market order.
        :param symbol: Trading pair (e.g., 'BTC/USDT').
        :param side: 'buy' or 'sell'.
        :param size: Order size.
        :return: Order response.
        """
        try:
            order = self.api.place_order(symbol, side, order_type="market", size=size)
            logging.info(f"✅ Market Order Placed: {order}")
            return order
        except Exception as e:
            logging.error(f"❌ Market Order Failed: {e}")
            return None

    def place_limit_order(self, symbol, side, size, price):
        """
        Places a limit order.
        :param symbol: Trading pair (e.g., 'BTC/USDT').
        :param side: 'buy' or 'sell'.
        :param size: Order size.
        :param price: Limit price.
        :return: Order response.
        """
        try:
            order = self.api.place_order(symbol, side, order_type="limit", size=size, price=price)
            logging.info(f"✅ Limit Order Placed: {order}")
            return order
        except Exception as e:
            logging.error(f"❌ Limit Order Failed: {e}")
            return None

    def cancel_order(self, order_id):
        """
        Cancels an existing order.
        :param order_id: The order ID to cancel.
        :return: Cancellation response.
        """
        try:
            response = self.api.cancel_order(order_id)
            logging.info(f"🚫 Order Cancelled: {order_id}")
            return response
        except Exception as e:
            logging.error(f"❌ Cancel Order Failed: {e}")
            return None

    def get_order_status(self, order_id):
        """
        Retrieves the status of an order.
        :param order_id: The order ID to check.
        :return: Order status response.
        """
        try:
            status = self.api.get_order_status(order_id)
            logging.info(f"📊 Order Status: {status}")
            return status
        except Exception as e:
            logging.error(f"❌ Fetch Order Status Failed: {e}")
            return None

# Example usage
if __name__ == "__main__": 
    trader = TradeExecution()
    symbol = "BTC/USDT"
    trader.place_market_order(symbol, "buy", 0.001)  # Buy 0.001 BTC at market price
