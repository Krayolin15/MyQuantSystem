import backtrader as bt
import yfinance as yf
import pandas as pd

class AdvancedStrategy(bt.Strategy):
    params = (('fast_length', 10), ('slow_length', 30), ('printlog', False),)

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.sma_fast = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.fast_length)
        self.sma_slow = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.slow_length)
        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)

    def next(self):
        if self.order: return
        if not self.position:
            if self.crossover > 0: self.order = self.buy()
        elif self.crossover < 0:
            self.order = self.sell()

def run_backtest(ticker, start, end, fast, slow):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(AdvancedStrategy, fast_length=fast, slow_length=slow)

    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if df.empty: raise ValueError("No data found for this ticker.")

    data_feed = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data_feed)

    # Set Initial Cash to R1,000,000
    cerebro.broker.setcash(1000000.0)
    cerebro.broker.setcommission(commission=0.001)

    strat_runs = cerebro.run()
    strat = strat_runs[0]

    # Sync Backtrader data with Pandas for Streamlit
    df['Fast_SMA'] = pd.Series(list(strat.sma_fast.get(size=len(df))), index=df.index)
    df['Slow_SMA'] = pd.Series(list(strat.sma_slow.get(size=len(df))), index=df.index)
    df['Crossover'] = pd.Series(list(strat.crossover.get(size=len(df))), index=df.index)

    return df, cerebro.broker.getvalue()
