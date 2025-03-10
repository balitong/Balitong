import logging
import time
from trading_bot.core.order_executor import OrderExecutor
from trading_bot.core.risk_manager import RiskManager
from trading_bot.core.signal_processor import SignalProcessor
from trading_bot.config import TRADE_SYMBOL, TRADE_QUANTITY

class TradeManager:
    """Handles automated trading execution based on AI signals."""

    def __init__(self):
        """Initializes the trade manager with order execution, signals, and risk control."""
        self.executor = OrderExecutor()
        self.risk_manager = RiskManager()
        self.signal_processor = SignalProcessor()
        self.current_position = None  # Tracks open positions

    def place_trade(self, trade_id, trade_details):
        # Place a new trade
        self.trades[trade_id] = trade_details
        return f"Trade {trade_id} placed successfully."

    def cancel_trade(self, trade_id):
        # Cancel an existing trade
        if trade_id in self.trades:
            del self.trades[trade_id]
            return f"Trade {trade_id} canceled successfully."
        else:
            return f"Trade {trade_id} not found."

    def get_trade_status(self, trade_id):
        # Get the status of a trade
        if trade_id in self.trades:
            return f"Trade {trade_id} status: {self.trades[trade_id]}"
        else:
            return f"Trade {trade_id} not found."

    def execute_trade(self):
        """
        Main function that listens to AI signals and executes trades accordingly.
        """
        try:
            logging.info("🔄 Checking AI trading signals...")
            signal = self.signal_processor.get_trade_signal()

            if signal is None:
                logging.info("⏳ No clear trade signal. Waiting for next analysis.")
                return

            side, price_prediction = signal['side'], signal['price']
            logging.info(f"📈 Signal received: {side.upper()} at projected price {price_prediction}")

            # Check risk management rules before placing a trade
            if not self.risk_manager.validate_trade(side):
                logging.warning("🚨 Trade blocked by risk management rules.")
                return

            # Decide trade type (Market or Limit)
            if side == "buy":
                order = self.executor.place_market_order(TRADE_SYMBOL, "buy", TRADE_QUANTITY)
            elif side == "sell":
                order = self.executor.place_market_order(TRADE_SYMBOL, "sell", TRADE_QUANTITY)
            else:
                logging.warning("⚠️ Invalid trade signal received.")
                return

            # Track position status
            if order and "orderId" in order:
                self.current_position = order
                logging.info(f"✅ Trade executed successfully. Order ID: {order['orderId']}")
            else:
                logging.error("❌ Trade execution failed.")

        except Exception as e:
            logging.error(f"❌ Error in trade execution: {e}")

    def monitor_positions(self):
        """
        Continuously checks the status of open positions and closes them if needed.
        """
        if not self.current_position:
            logging.info("🔍 No open positions to monitor.")
            return

        order_id = self.current_position.get("orderId")
        if not order_id:
            return

        status = self.executor.get_order_status(order_id)
        if status and status.get("status") == "FILLED":
            logging.info(f"✅ Order {order_id} has been FILLED. Updating records.")
            self.current_position = None  # Reset after trade completion
        elif status and status.get("status") == "CANCELLED":
            logging.info(f"⚠️ Order {order_id} was CANCELLED. Resetting position.")
            self.current_position = None

    def run(self):
        """
        Runs the automated trading bot loop.
        """
        logging.info("🚀 Starting Trade Manager...")
        while True:
            self.execute_trade()
            self.monitor_positions()
            time.sleep(10)  # Wait before checking for new signals
