import logging
import time
from trading_bot.config import BITGET_API_KEY, BITGET_SECRET_KEY, BITGET_PASSPHRASE
from trading_bot.core.exchange_client import BitgetClient

class OrderExecutor:
    """Handles executing and managing orders on Bitget."""

    def __init__(self):
        """Initializes the order executor with the Bitget client."""
        self.client = BitgetClient(BITGET_API_KEY, BITGET_SECRET_KEY, BITGET_PASSPHRASE)

    def place_market_order(self, symbol, side, quantity):
        """
        Places a market order.

        :param symbol: str - Trading pair (e.g., 'PIUSDT').
        :param side: str - 'buy' or 'sell'.
        :param quantity: float - Amount to trade.
        :return: dict - API response.
        """
        try:
            logging.info(f"📢 Placing MARKET {side.upper()} order for {quantity} {symbol}...")
            order = self.client.place_order(
                symbol=symbol,
                side=side,
                order_type="market",
                quantity=quantity
            )
            logging.info(f"✅ Market order executed: {order}")
            return order
        except Exception as e:
            logging.error(f"❌ Market order failed: {e}")
            return None

    def place_limit_order(self, symbol, side, quantity, price):
        """
        Places a limit order.

        :param symbol: str - Trading pair (e.g., 'PIUSDT').
        :param side: str - 'buy' or 'sell'.
        :param quantity: float - Amount to trade.
        :param price: float - Price to set the limit order.
        :return: dict - API response.
        """
        try:
            logging.info(f"📢 Placing LIMIT {side.upper()} order for {quantity} {symbol} at {price}...")
            order = self.client.place_order(
                symbol=symbol,
                side=side,
                order_type="limit",
                quantity=quantity,
                price=price
            )
            logging.info(f"✅ Limit order placed: {order}")
            return order
        except Exception as e:
            logging.error(f"❌ Limit order failed: {e}")
            return None

    def cancel_order(self, order_id):
        """
        Cancels an existing order.

        :param order_id: str - ID of the order to cancel.
        :return: dict - API response.
        """
        try:
            logging.info(f"🔄 Cancelling order {order_id}...")
            response = self.client.cancel_order(order_id)
            logging.info(f"✅ Order cancelled: {response}")
            return response
        except Exception as e:
            logging.error(f"❌ Order cancellation failed: {e}")
            return None

    def get_order_status(self, order_id):
        """
        Retrieves the status of an order.

        :param order_id: str - ID of the order.
        :return: dict - API response.
        """
        try:
            order_status = self.client.get_order(order_id)
            logging.info(f"📊 Order status: {order_status}")
            return order_status
        except Exception as e:
            logging.error(f"❌ Failed to get order status: {e}")
            return None
