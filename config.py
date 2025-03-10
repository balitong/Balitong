# Trading Pairs for Backtesting
TRADING_PAIRS = [
    "pi_usdt", "btc_usdt", "eth_usdt", "sol_usdt",
    "bnb_usdt", "xrp_usdt", "doge_usdt", "avax_usdt"
]

# Data Paths
RAW_DATA_PATH = "data/raw/"
PROCESSED_DATA_PATH = "data/processed/"

# Model Paths
MODEL_PATHS = {
    "lstm": "models/lstm_model.pth",
    "cnn": "models/cnn_model.pth",
    "hybrid": "models/hybrid_lstm_cnn.pth"
}

# AI Model Parameters
LSTM_EPOCHS = 50
CNN_EPOCHS = 50
HYBRID_EPOCHS = 100
LEARNING_RATE = 0.001
BATCH_SIZE = 64

# Result Paths
RESULTS_PATH = "results/"

# Backtesting Settings
START_BALANCE = 1000  # Starting USDT balance for backtesting
TRADE_FEE = 0.001  # 0.1% trading fee
SLIPPAGE = 0.0005  # 0.05% slippage for market orders
RISK_PER_TRADE = 0.02  # Risk 2% of capital per trade
TIMEFRAMES = ["5m", "15m", "1h", "4h"]  # Timeframes to test
