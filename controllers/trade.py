import logging
import numpy as np
from config.vars import short_term_window, long_term_window

class TradeModel:
    def __init__(self, initial_capital):
        self.capital = initial_capital
        self.holding_quantity = 0
        self.average_price = 0

    def buy_stock(self, price, quantity):
        quantity = min(quantity, (self.capital // price) // 100 * 100)  # 100株単位に調整
        if quantity > 0:
            self.capital -= quantity * price
            self.holding_quantity += quantity
            self.average_price = ((self.average_price * (self.holding_quantity - quantity)) + (price * quantity)) / self.holding_quantity
            logging.info(f"Bought {quantity} shares at {price} each. New capital: {self.capital}, Holding: {self.holding_quantity}, Average purchase price: {self.average_price}")

    def sell_stock(self, price, quantity):
        quantity = min(quantity, (self.holding_quantity // 100) * 100)  # 100株単位に調整
        if quantity > 0:
            self.capital += quantity * price
            self.holding_quantity -= quantity
            if self.holding_quantity == 0:
                self.average_price = 0
            logging.info(f"Sold {quantity} shares at {price} each. New capital: {self.capital}, Holding: {self.holding_quantity}, Average purchase price: {self.average_price}")

class TradeController:
    def __init__(self, df, symbol, initial_capital):
        self.model = TradeModel(initial_capital)
        self.logger = logging.getLogger()
        self.symbol = symbol
        self.historical_prices = self.get_daily_prices(df)
        self.short_term_ma = self.calculate_moving_average(self.historical_prices, short_term_window)
        self.long_term_ma = self.calculate_moving_average(self.historical_prices, long_term_window)

    def get_daily_prices(self, df):
        try:
            daily_df = df['close'].resample('D').last().dropna()
            prices = daily_df.values  # リストではなくNumPy配列を使用
            return prices
        except Exception as e:
            self.logger.error(f"Error loading daily prices: {e}")
            return np.array([])

    def calculate_moving_average(self, prices, window):
        if len(prices) < window:
            return None
        cumsum = np.cumsum(np.insert(prices, 0, 0))
        moving_avg = (cumsum[window:] - cumsum[:-window]) / float(window)
        return moving_avg

    def trading_logic(self, current_price, upper_limit, lower_limit):
        action, quantity = None, 0

        if len(self.historical_prices) < long_term_window:
            self.logger.error("Not enough historical data to calculate moving averages.")
            return action, quantity

        short_term_ma = self.short_term_ma[-1] if self.short_term_ma is not None else None
        long_term_ma = self.long_term_ma[-1] if self.long_term_ma is not None else None

        if short_term_ma is None or long_term_ma is None:
            self.logger.error("Error calculating moving averages.")
            return action, quantity

        self.logger.info(f"Short-term MA: {short_term_ma}, Long-term MA: {long_term_ma}")
        self.logger.info(f"Before Action - Capital: {self.model.capital}, Holding Quantity: {self.model.holding_quantity}, Average Price: {self.model.average_price}")

        if self.model.holding_quantity == 0:
            quantity = (self.model.capital // current_price) // 100 * 100  # 100株単位に調整
            if quantity > 0:
                action = 'buy'
            else:
                self.logger.error(f"Not enough capital to buy at price {current_price}.")
        else:
            if current_price >= self.model.average_price * upper_limit and short_term_ma > long_term_ma:
                action, quantity = 'sell', (self.model.holding_quantity // 100) * 100  # 100株単位に調整
            elif current_price <= self.model.average_price * lower_limit:
                action, quantity = 'sell', (self.model.holding_quantity // 100) * 100  # 100株単位に調整

        self.logger.info(f"After Action - Capital: {self.model.capital}, Holding Quantity: {self.model.holding_quantity}, Average Price: {self.model.average_price}")
        self.logger.info(f"Action: {action}, Quantity: {quantity}, Price: {current_price}")
        return action, quantity
