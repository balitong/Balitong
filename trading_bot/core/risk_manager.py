import logging

class RiskManager:
    """Handles risk management, stop-loss, and take-profit strategies."""

    def __init__(self, stop_loss_pct=2, take_profit_pct=5, max_daily_loss_pct=10, max_risk_per_trade=1):
        """
        Initializes risk management settings.
        
        :param stop_loss_pct: float - Stop-loss percentage (default: 2%).
        :param take_profit_pct: float - Take-profit percentage (default: 5%).
        :param max_daily_loss_pct: float - Max daily loss before stopping trading (default: 10%).
        :param max_risk_per_trade: float - Maximum risk per trade as a percentage of the account balance (default: 1%).
        """
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.max_daily_loss_pct = max_daily_loss_pct
        self.max_risk_per_trade = max_risk_per_trade
        self.daily_loss = 0  # Track daily losses

    def calculate_stop_loss(self, entry_price):
        """
        Calculates the stop-loss price.
        
        :param entry_price: float - The entry price of the trade.
        :return: float - The stop-loss price.
        """
        stop_loss_price = entry_price * (1 - self.stop_loss_pct / 100)
        logging.info(f"⚠️ Stop-loss set at: {stop_loss_price}")
        return round(stop_loss_price, 6)

    def calculate_take_profit(self, entry_price):
        """
        Calculates the take-profit price.
        
        :param entry_price: float - The entry price of the trade.
        :return: float - The take-profit price.
        """
        take_profit_price = entry_price * (1 + self.take_profit_pct / 100)
        logging.info(f"💰 Take-profit set at: {take_profit_price}")
        return round(take_profit_price, 6)

    def update_daily_loss(self, loss_amount):
        """
        Updates the daily loss tracker.
        
        :param loss_amount: float - Amount lost in the trade.
        :return: bool - Whether trading should be paused due to max daily loss.
        """
        self.daily_loss += loss_amount
        logging.warning(f"📉 Updated daily loss: {self.daily_loss}%")

        if self.daily_loss >= self.max_daily_loss_pct:
            logging.critical("⛔ Max daily loss limit reached! Trading paused.")
            return True  # Indicate that trading should stop
        return False  # Continue trading

    def calculate_position_size(self, account_balance: float, stop_loss: float) -> float:
        """
        Calculate the position size based on the account balance and stop loss.

        :param account_balance: The current account balance.
        :param stop_loss: The stop loss amount per trade.
        :return: The position size.
        """
        risk_amount = account_balance * (self.max_risk_per_trade / 100)
        position_size = risk_amount / stop_loss
        return position_size

    def set_max_risk_per_trade(self, max_risk: float):
        self.max_risk_per_trade = max_risk

    def set_max_daily_loss(self, max_loss: float):
        self.max_daily_loss = max_loss

    def check_risk(self, potential_loss: float) -> bool:
        if potential_loss > self.max_risk_per_trade:
            return False
        if self.current_daily_loss + potential_loss > self.max_daily_loss:
            return False
        return True

    def reset_daily_loss(self):
        self.current_daily_loss = 0.0
