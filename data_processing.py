import pandas as pd
import os
from config import TRADING_PAIRS, RAW_DATA_PATH, PROCESSED_DATA_PATH
from trading_bot.exchange.order_execution import place_order

# Ensure required libraries are installed
# pip install pandas

def clean_data(symbol):
    """Load, clean, and save processed data."""
    file_path = f"{RAW_DATA_PATH}{symbol}.csv"

    if not os.path.exists(file_path):
        print(f"⚠️ Skipping {symbol} (file not found).")
        return
    
    df = pd.read_csv(file_path)

    # Ensure required columns exist
    required_columns = {"timestamp", "open", "high", "low", "close", "volume"}
    if not required_columns.issubset(df.columns):
        print(f"⚠️ Skipping {symbol} (invalid columns).")
        return

    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Drop NaN values
    df.dropna(inplace=True)

    # Normalize price data (0-1 scale for AI training)
    for col in ["open", "high", "low", "close"]:
        df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

    # Ensure output directory exists
    os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)

    # Save cleaned file
    processed_file = f"{PROCESSED_DATA_PATH}{symbol}_clean.csv"
    df.to_csv(processed_file, index=False)
    print(f"✅ Processed {symbol} -> {processed_file}")

# Process all pairs
for pair in TRADING_PAIRS:
    clean_data(pair)

print("✅ Data processing complete!")

# Train AI model
os.system("python e:\\Signal\\trading_bot\\ai_training\\train_ai.py")

# Place orders based on AI model predictions
for pair in TRADING_PAIRS:
    place_order(pair, "buy", "market", size=0.1)  # Example market buy
    time.sleep(1)  # Avoid API rate limits

print("✅ Order execution completed!")
