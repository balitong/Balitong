import logging
import threading
import time
from trading_bot.data.market_data import MarketData
from trading_bot.execution.trade_execution import TradeExecution
from trading_bot.risk.risk_management import RiskManagement

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class BotController:
    """Controls AI trading bot operations, including execution, monitoring, and shutdown."""

    def __init__(self, trading_pairs, stop_loss_pct=2, take_profit_pct=5, max_daily_loss=100):
        """
        Initializes bot with risk management and trade execution.
        :param trading_pairs: List of trading pairs (e.g., ['BTC/USDT', 'ETH/USDT']).
        :param stop_loss_pct: Stop-loss percentage per trade.
        :param take_profit_pct: Take-profit percentage per trade.
        :param max_daily_loss: Maximum daily loss allowed (in USDT).
        """
        self.trading_pairs = trading_pairs
        self.market_data = MarketData()
        self.trade_execution = TradeExecution()
        self.risk_management = RiskManagement(max_daily_loss, stop_loss_pct, take_profit_pct)
        self.running = False
        self.bot_thread = None

    def start_trading(self):
        """Starts the AI trading bot in a separate thread."""
        if not self.running:
            self.running = True
            self.bot_thread = threading.Thread(target=self._trade_loop)
            self.bot_thread.start()
            logging.info("🚀 Trading bot started successfully!")

    def stop_trading(self):
        """Stops the AI trading bot."""
        self.running = False
        if self.bot_thread:
            self.bot_thread.join()
        logging.info("🛑 Trading bot stopped.")

    def _trade_loop(self):
        """Main loop for trading execution and monitoring."""
        while self.running:
            for symbol in self.trading_pairs:
                logging.info(f"📊 Fetching market data for {symbol}...")
                current_price = self.market_data.get_latest_price(symbol)
                logging.info(f"💰 {symbol} Current Price: {current_price}")

                if self.risk_management.check_daily_loss():
                    self.stop_trading()
                    break

                # Simulated AI decision logic (can be replaced with AI model)
                trade_signal = self._ai_trade_decision(symbol, current_price)

                if trade_signal == "buy":
                    logging.info(f"🟢 BUY Signal for {symbol}")
                    order_id = self.trade_execution.place_market_order(symbol, "buy", size=0.001)
                    self.risk_management.monitor_trade(symbol, entry_price=current_price, order_id=order_id)

                elif trade_signal == "sell":
                    logging.info(f"🔴 SELL Signal for {symbol}")
                    self.trade_execution.place_market_order(symbol, "sell", size=0.001)

            time.sleep(10)  # Pause before checking market again

    def _ai_trade_decision(self, symbol, current_price):
        """
        Simulated AI trade decision logic.
        :param symbol: Trading pair (e.g., 'BTC/USDT').
        :param current_price: Latest market price.
        :return: 'buy', 'sell', or 'hold'
        """
        # Placeholder: Implement AI logic here
        return "hold"

# Example usage
if __name__ == "__main__":
    bot = BotController(trading_pairs=["BTC/USDT", "ETH/USDT"], stop_loss_pct=2, take_profit_pct=5, max_daily_loss=100)
    bot.start_trading()
    time.sleep(30)  # Let it run for 30 seconds
    bot.stop_trading()
