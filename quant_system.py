import backtrader as bt
import yfinance as yf
import pandas as pd
import datetime


# --- 1. THE STRATEGY ---
# This class defines the "Brain" of the trading system.
# It uses an event-driven approach (standard in HFT/Quant shops).
class AdvancedStrategy(bt.Strategy):
    params = (
        ('fast_length', 10),  # Fast Moving Average (10 days)
        ('slow_length', 30),  # Slow Moving Average (30 days)
        ('printlog', True),  # Enable logging
    )

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add Indicators (The Math)
        # We use Simple Moving Averages (SMA).
        # In a real advanced system, you might swap this for RSI, Bollinger, or ML signals.
        self.sma_fast = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.fast_length)
        self.sma_slow = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.slow_length)

        # The Crossover Signal (1 = Buy Signal, 0 = No Signal)
        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)

    def log(self, txt, dt=None):
        """ Logging function for this strategy"""
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()}, {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log(
                    f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log(f'OPERATION PROFIT, GROSS {trade.pnl:.2f}, NET {trade.pnlcomm:.2f}')

    def next(self):
        # Simply log the closing price of the series from the reference
        # self.log(f'Close, {self.dataclose[0]:.2f}')

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # Not yet ... we MIGHT BUY if ...
            if self.crossover > 0:  # Golden Cross (Fast crosses above Slow)
                self.log(f'BUY CREATE, {self.dataclose[0]:.2f}')
                self.order = self.buy()  # Buy current position size

        else:
            # Already in the market ... we MIGHT SELL if ...
            if self.crossover < 0:  # Death Cross (Fast crosses below Slow)
                self.log(f'SELL CREATE, {self.dataclose[0]:.2f}')
                self.order = self.sell()  # Sell everything


# --- 2. THE EXECUTION ENGINE ---
if __name__ == '__main__':
    # Create a cerebro entity (The Engine)
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(AdvancedStrategy)

    # --- REAL WORLD DATA INGESTION ---
    print("Downloading Real-World Data for AAPL...")
    # We download data using yfinance
    # Note: 'auto_adjust=True' corrects for stock splits and dividends!
    data_df = yf.download("AAPL", start="2020-01-01", end="2023-12-31", progress=False, auto_adjust=True)

    # We must ensure the index is a datetime (yfinance usually returns this, but good to be safe)
    # Check if data is multi-level column (fix for new yfinance versions)
    if isinstance(data_df.columns, pd.MultiIndex):
        data_df.columns = data_df.columns.get_level_values(0)

    # Create a Data Feed
    data = bt.feeds.PandasData(dataname=data_df)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    start_cash = 100000.0
    cerebro.broker.setcash(start_cash)

    # Set the commission - 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.001)

    # Print out the starting conditions
    print(f'Starting Portfolio Value: {cerebro.broker.getvalue():.2f}')

    # Run over everything
    cerebro.run()

    # Print out the final result
    final_value = cerebro.broker.getvalue()
    pnl = final_value - start_cash
    print(f'Final Portfolio Value: {final_value:.2f}')
    print(f'Total Profit/Loss: {pnl:.2f}')

    # Plot the result
    # Note: This requires matplotlib to be installed.
    cerebro.plot(style='candlestick')