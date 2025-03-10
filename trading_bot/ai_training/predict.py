import torch
import pandas as pd
import os
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import DataLoader, TensorDataset
from config import PROCESSED_DATA_PATH, MODEL_PATHS, BATCH_SIZE

# Ensure required libraries are installed
# pip install pandas numpy torch scikit-learn

# Define LSTM model (same as in train_ai.py)
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size=64, num_layers=2):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)  # Predict next price
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        return self.fc(lstm_out[:, -1, :])  # Output from last timestep

# Load and preprocess data
def load_data(symbol):
    file_path = f"{PROCESSED_DATA_PATH}{symbol}_clean.csv"

    if not os.path.exists(file_path):
        print(f"⚠️ Skipping {symbol} (file not found).")
        return None

    df = pd.read_csv(file_path)
    
    # Select features
    features = df[["open", "high", "low", "close", "volume"]].values

    # Normalize
    scaler = MinMaxScaler()
    features = scaler.fit_transform(features)

    # Convert to tensors
    X = torch.tensor(features, dtype=torch.float32)

    return DataLoader(TensorDataset(X), batch_size=BATCH_SIZE, shuffle=False)

# Predict next price
def predict(symbol):
    print(f"🔮 Predicting next price for {symbol}...")

    data_loader = load_data(symbol)
    if data_loader is None:
        return

    model = LSTMModel(input_size=5)  # 5 input features
    model.load_state_dict(torch.load(MODEL_PATHS["lstm"]))
    model.eval()

    predictions = []
    with torch.no_grad():
        for X_batch in data_loader:
            outputs = model(X_batch[0].unsqueeze(1))  # Add batch dimension
            predictions.extend(outputs.squeeze().tolist())

    return predictions

# Example usage
if __name__ == "__main__":
    symbol = "BTCUSD"  # Example trading pair
    predictions = predict(symbol)
    if predictions:
        print(f"Predictions for {symbol}: {predictions}")
