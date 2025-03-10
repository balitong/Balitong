import os
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from trading_bot.logs.data_logger import log_event
from trading_bot.data.trade_history import get_trade_history

# Ensure required libraries are installed
# pip install numpy pandas scikit-learn

# AI Model Storage Path
MODEL_FILE = "/trading_bot/ai/models/trade_prediction_model.pkl"

# Ensure model directory exists
if not os.path.exists("/trading_bot/ai/models"):
    os.makedirs("/trading_bot/ai/models")

def load_trade_data():
    """Loads trade history for AI training."""
    history = get_trade_history()
    if not history:
        log_event("⚠️ No trade history available for AI analysis.")
        return pd.DataFrame()

    df = pd.DataFrame(history)
    df["profit/loss"] = df["profit/loss"].astype(float)
    return df

def preprocess_data(df):
    """
    Preprocess trade data for AI model.

    :param df: DataFrame containing trade data
    :return: Features and target variables
    """
    # Example preprocessing steps
    df['target'] = df['profit/loss'].apply(lambda x: 1 if x > 0 else 0)
    features = df.drop(columns=['profit/loss', 'target'])
    target = df['target']
    return features, target

def train_model(features, target):
    """
    Train a RandomForest model on the trade data.

    :param features: Features for training
    :param target: Target variable for training
    :return: Trained model
    """
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")
    return model

def predict_trade(model, trade_data):
    """
    Predict the outcome of a trade using the trained model.

    :param model: Trained model
    :param trade_data: Data for the trade to predict
    :return: Prediction result
    """
    return model.predict([trade_data])

def train_ai_model():
    """Trains an AI model on past trade data."""
    df = load_trade_data()
    if df.empty:
        return None

    df["target"] = (df["profit/loss"] > 0).astype(int)  # 1 for profit, 0 for loss
    features = df.drop(columns=["profit/loss", "target"])
    labels = df["target"]

    scaler = MinMaxScaler()
    features_scaled = scaler.fit_transform(features)

    X_train, X_test, y_train, y_test = train_test_split(features_scaled, labels, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    with open(MODEL_FILE, "wb") as file:
        import pickle
        pickle.dump(model, file)

    log_event("✅ AI model trained and saved successfully.")
    return model

# Example usage
if __name__ == "__main__":
    df = load_trade_data()
    features, target = preprocess_data(df)
    model = train_model(features, target)
    example_trade = features.iloc[0].values
    prediction = predict_trade(model, example_trade)
    print(f"Trade Prediction: {'Profit' if prediction[0] == 1 else 'Loss'}")
