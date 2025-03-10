import sys
import threading
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox
from PyQt5.QtCore import Qt
from trading_bot.controller.bot_controller import TradingBot

class TradingBotGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.bot = TradingBot()
        self.init_ui()

    def init_ui(self):
        """Initialize the GUI layout."""
        self.setWindowTitle("Super AI Trading Bot")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.status_label = QLabel("⚡ Status: Stopped", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Dropdown for selecting mode
        self.mode_selector = QComboBox(self)
        self.mode_selector.addItems(["Manual", "Semi-Auto", "Full-Auto"])
        layout.addWidget(self.mode_selector)

        # Start & Stop buttons
        self.start_button = QPushButton("🚀 Start Trading", self)
        self.start_button.clicked.connect(self.start_bot)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("🛑 Stop Trading", self)
        self.stop_button.clicked.connect(self.stop_bot)
        layout.addWidget(self.stop_button)

        # Live price updates
        self.price_label = QLabel("📊 Live Price: Waiting...", self)
        self.price_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.price_label)

        self.setLayout(layout)

    def start_bot(self):
        """Start the bot in the selected mode."""
        selected_mode = self.mode_selector.currentText().lower()
        self.status_label.setText(f"✅ Running in {selected_mode.capitalize()} Mode")
        threading.Thread(target=self.run_bot, args=(selected_mode,), daemon=True).start()

    def stop_bot(self):
        """Stop the bot."""
        self.bot.stop()
        self.status_label.setText("⚡ Status: Stopped")

    def run_bot(self, mode):
        """Run the bot and update live prices."""
        self.bot.start(mode)
        while self.bot.running:
            try:
                symbol = self.bot.trading_pairs[0]  # Display first trading pair price
                current_price = self.bot.get_live_price(symbol)
                self.price_label.setText(f"📊 Live Price ({symbol}): {current_price}")
                time.sleep(5)  # Update every 5 seconds
            except Exception as e:
                self.price_label.setText("❌ Error fetching price")

# Run GUI
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TradingBotGUI()
    window.show()
    sys.exit(app.exec_())
