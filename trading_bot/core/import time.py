import time
import logging
from core.trade_engine import TradeEngine
from core.config import Config
from core.market_data import MarketData
from core.trade_data import TradeData

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    """Main loop to run the trading bot."""
    logging.info("🚀 Starting Super AI Trading Bot...")
    
    config = Config()
    trade_engine = TradeEngine()
    market_data = MarketData()
    trade_data = TradeData()
    total_trades = 0  # Initialize trade counter

    try:
        while True:
            # 1️⃣ Fetch latest market data
            latest_prices = market_data.get_latest_prices()

            # 2️⃣ Select trading pairs based on volatility analysis
            selected_pairs = market_data.select_high_volatility_pairs(latest_prices)

            # 3️⃣ Process trading logic for each selected pair
            for pair in selected_pairs:
                try:
                    # Fetch price data
                    price = latest_prices[pair]
                    logging.info(f"📈 Processing {pair} at {price}")

                    # Execute trade decision
                    trade_engine.execute_trade(pair, price)
                    total_trades += 1  # Increment trade counter

                except Exception as e:
                    logging.error(f"❌ Error processing {pair}: {e}")

            # 4️⃣ Check daily loss and stop if limit exceeded
            daily_loss = trade_data.get_daily_loss()
            if daily_loss >= config.max_daily_loss:
                logging.warning("⛔ Maximum daily loss reached. Stopping trades for today.")
                break

            # ⏳ Wait before next cycle
            time.sleep(config.execution_interval)

    except KeyboardInterrupt:
        logging.info("🛑 Bot stopped manually.")
    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
    finally:
        logging.info(f"🔢 Total trades executed: {total_trades}")  # Log total trades

if __name__ == "__main__":
    main()
