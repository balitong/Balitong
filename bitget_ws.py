import websocket
import json
import time

# Define your WebSocket URL
url = "wss://ws.bitget.com/spot/v1/stream"

# Define the subscription message for the symbol you're interested in
data = {
    "op": "subscribe",
    "args": [{
        "channel": "spot/candle60s",  # Change to your channel, e.g., "spot/ticker"
        "instId": "BTCUSDT"  # Modify the instrument ID as needed
    }]
}

# Define the function to handle messages from WebSocket
def on_message(ws, message):
    print(f"Received message: {message}")
    
# Define the function to handle errors
def on_error(ws, error):
    print(f"Error: {error}")
    
# Define the function to handle the WebSocket connection closure
def on_close(ws, close_status_code, close_msg):
    print("Closed connection")

# Define the function to handle the opening of WebSocket connection
def on_open(ws):
    print("Connection opened, sending subscribe message...")
    ws.send(json.dumps(data))

# Try to create and run the WebSocket connection
def run_websocket():
    try:
        print("Attempting to connect to Bitget WebSocket...")
        ws = websocket.WebSocketApp(url, 
                                    on_message=on_message, 
                                    on_error=on_error, 
                                    on_close=on_close, 
                                    on_open=on_open)
        
        ws.run_forever(ping_interval=30, ping_timeout=10)  # Keep connection alive with pings
    except Exception as e:
        print(f"Error in WebSocket connection: {e}")

# Run WebSocket and keep checking for success/fail
while True:
    run_websocket()
    print("Reconnecting in 5 seconds...")
    time.sleep(5)
