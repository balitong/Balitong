import logging
import time
import signal
from trading_bot.core.bot_controller import BotController

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    """Main function to start the AI trading bot."""
    logging.info("🚀 Starting AI Auto-Trading Bot...")

    # Define trading pairs and risk management settings
    trading_pairs = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "ADA/USDT", "BNB/USDT", "DOT/USDT", "LINK/USDT"]
    stop_loss_pct = 2  # Stop-loss at 2%
    take_profit_pct = 5  # Take-profit at 5%
    max_daily_loss = 100  # Max daily loss limit in USDT

    # Initialize and start the bot
    bot = BotController(trading_pairs, stop_loss_pct, take_profit_pct, max_daily_loss)
    bot.start_trading()

    def handle_exit(signum, frame):
        logging.info("🛑 Stopping AI Auto-Trading Bot...")
        bot.stop_trading()
        exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    try:
        while True:
            time.sleep(10)  # Keep the bot running
    except KeyboardInterrupt:
        handle_exit(None, None)

if __name__ == "__main__":
    main()
