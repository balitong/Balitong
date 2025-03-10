import websocket
import json

class BitgetWebSocketClient:
    def __init__(self, url, on_message, on_error, on_close):
        self.url = url
        self.on_message = on_message
        self.on_error = on_error
        self.on_close = on_close
        self.ws = None

    def connect(self):
        self.ws = websocket.WebSocketApp(
            self.url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws.on_open = self.on_open
        self.ws.run_forever()

    def on_open(self, ws):
        print("WebSocket connection opened")

    def send_message(self, message):
        self.ws.send(json.dumps(message))

    def close(self):
        self.ws.close()
