import time
import threading
from config import TRADING_MODE, AUTO_TRADE_INTERVAL
from exchange.order_execution import execute_trade
from system_health import monitor_system_health
from risk_management import check_daily_loss_limit

class BotController:
    def __init__(self, strategy, broker):
        self.strategy = strategy
        self.broker = broker
        self.running = False
        self.trade_thread = None

    def start(self):
        if self.running:
            print("⚠️ Trading bot is already running!")
            return

        print("🚀 Starting Trading Bot...")
        self.running = True
        self.trade_thread = threading.Thread(target=self.run)
        self.trade_thread.start()

    def stop(self):
        if not self.running:
            print("⚠️ Trading bot is not running!")
            return

        print("⏹️ Stopping Trading Bot...")
        self.running = False
        if self.trade_thread:
            self.trade_thread.join()

    def run(self):
        while self.running:
            print("🔄 Checking system health...")
            if not monitor_system_health():
                print("❌ System health check failed. Stopping bot.")
                self.stop()
                break

            print("📊 Running trade cycle...")
            if check_daily_loss_limit(0):
                print("❌ Max daily loss reached. Trading paused.")
                self.stop()
                break

            self.execute_trade()
            time.sleep(AUTO_TRADE_INTERVAL)

    def execute_trade(self):
        trade_signal = self.strategy.generate_signal()
        if trade_signal:
            self.broker.execute(trade_signal)

# Example usage
if __name__ == "__main__":
    # ...existing code...
    bot = BotController(strategy=None, broker=None)  # Replace with actual strategy and broker
    bot.start()

    # Run bot for a few cycles before stopping
    time.sleep(30)
    bot.stop()
