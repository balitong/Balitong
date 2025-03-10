import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import os
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import DataLoader, TensorDataset
from config import TRADING_PAIRS, PROCESSED_DATA_PATH, MODEL_PATHS, LSTM_EPOCHS, LEARNING_RATE, BATCH_SIZE
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle

# Ensure required libraries are installed
# pip install torch pandas numpy scikit-learn

# Define LSTM model
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
    
    # Select features & target (predict next close price)
    features = df[["open", "high", "low", "close", "volume"]].values
    targets = df["close"].shift(-1).fillna(0).values  # Next timestep close

    # Normalize
    scaler = MinMaxScaler()
    features = scaler.fit_transform(features)

    # Convert to tensors
    X = torch.tensor(features[:-1], dtype=torch.float32)  # Remove last row
    y = torch.tensor(targets[:-1], dtype=torch.float32).view(-1, 1)

    return DataLoader(TensorDataset(X, y), batch_size=BATCH_SIZE, shuffle=True)

def load_data_rf(symbol):
    file_path = f"{PROCESSED_DATA_PATH}{symbol}_clean.csv"
    if not os.path.exists(file_path):
        print(f"⚠️ Skipping {symbol} (file not found).")
        return None
    return pd.read_csv(file_path)

# Train LSTM model
def train_lstm(symbol):
    print(f"📈 Training LSTM model for {symbol}...")

    data_loader = load_data(symbol)
    if data_loader is None:
        return

    model = LSTMModel(input_size=5)  # 5 input features
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # Training loop
    for epoch in range(LSTM_EPOCHS):
        for X_batch, y_batch in data_loader:
            optimizer.zero_grad()
            outputs = model(X_batch.unsqueeze(1))  # Add batch dimension
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()

        if (epoch + 1) % 10 == 0:
            print(f"📊 Epoch {epoch+1}/{LSTM_EPOCHS}, Loss: {loss.item():.6f}")

    # Ensure directory exists
    os.makedirs(os.path.dirname(MODEL_PATHS["lstm"]), exist_ok=True)

    # Save model
    torch.save(model.state_dict(), MODEL_PATHS["lstm"])
    print(f"✅ LSTM model saved -> {MODEL_PATHS['lstm']}")

# Train RandomForest model
def train_rf(symbol):
    df = load_data_rf(symbol)
    if df is None:
        return

    # Prepare features and target
    X = df[["open", "high", "low", "close", "volume"]]
    y = (df["close"].shift(-1) > df["close"]).astype(int)  # Example target: next day price increase

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"✅ RandomForest model trained for {symbol} with accuracy: {accuracy:.2f}")

    # Save model
    model_path = f"{PROCESSED_DATA_PATH}{symbol}_rf_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f"✅ RandomForest model saved: {model_path}")

# Train AI for all pairs
for pair in TRADING_PAIRS:
    train_lstm(pair)
    train_rf(pair)

print("✅ AI training complete!")
