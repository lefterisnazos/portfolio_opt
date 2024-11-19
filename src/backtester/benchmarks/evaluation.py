from src.backtester.benchmarks.base import Benchmark
import numpy as np
import pandas as pd


class PNL(Benchmark):

    """"
    First 3 lines of calculate function should be implemented in every calculation function, in order to be able to compare weight_allocations and daily_returns
    """
    def __init__(self, freq='D'):
        super(PNL, self).__init__(name="PNL (%)", freq=freq)


    def calculate(self, weight_predictions, ticker_list, data, **kwargs):

        """
        EJ lecture: log(1+x) = x approximately, for small x. SO if we use cumsum() on returns we approximate the cumulative return
        more precisely: log(total_ret) = log((1+r1)*(1+r2)*...*(1_r_n)) = log(1+r1) + log(1+r2) + ... + log(1+r_n) = r1 + r2 + rn returns
        """

        daily_returns = data.pct_change().fillna(0)

        portfolio_returns = (weight_predictions * daily_returns).sum(axis=1)
        # portfolio_returns_cumsum = portfolio_pnl.cumsum()
        portfolio_returns_df = portfolio_returns.to_frame(name=self.name)

        grouped_pnl = self.groupby_freq(portfolio_returns_df, self.freq).sum()*100
        grouped_pnl = self.to_frame_and_indexing(grouped_pnl, self.freq, self.name)

        return (grouped_pnl)

class Sharpe(Benchmark):

    def __init__(self, freq='D', risk_free_rate=0):
        super(Sharpe, self).__init__(name="Sharpe", freq=freq)
        self.risk_free_rate = risk_free_rate

    def calculate(self, weight_predictions, ticker_list, data, **kwargs):

        daily_returns = data.pct_change().fillna(0)
        portfolio_returns = (weight_predictions * daily_returns).sum(axis=1)

        excess_returns = portfolio_returns - self.risk_free_rate
        grouped_returns = self.groupby_freq(excess_returns, self.freq)
        mean = grouped_returns.mean()
        std = grouped_returns.std()
        sharpe_ratio = mean / std

        sharpe_ratio_df = self.to_frame_and_indexing(sharpe_ratio, self.freq, self.name)
        #sharpe_ratio_df = sharpe_ratio_df.replace([float('inf'), float('-inf')], 0).fillna(0)# Use the class name here

        return sharpe_ratio_df


class MaxDrawdown(Benchmark):

    def __init__(self, freq='D'):
        super(MaxDrawdown, self).__init__(name="MaxDrawdown", freq=freq)

    def calculate(self, weight_predictions, ticker_list, data, **kwargs):

        daily_returns = data.pct_change().fillna(0)
        portfolio_returns = (weight_predictions * daily_returns).sum(axis=1)

        cumulative_returns = (1 + portfolio_returns).cumprod()

        rolling_max = cumulative_returns.cummax()
        drawdowns = (cumulative_returns - rolling_max) / rolling_max

        drawdown_df = drawdowns.to_frame(name="Drawdown")

        return drawdown_df.reindex(data.index).fillna(0)


class Volatility(Benchmark):

    def __init__(self, freq='D', window=20):
        super(Volatility, self).__init__(name="Volatility", freq=freq)
        self.window = window  # Default rolling window is 20 days

    def calculate(self, weight_predictions, ticker_list, data, **kwargs):

        daily_returns = data.pct_change().fillna(0)
        portfolio_returns = (weight_predictions * daily_returns).sum(axis=1)

        rolling_volatility = portfolio_returns.rolling(self.window).std()

        volatility_df = rolling_volatility.to_frame(name="Volatility")

        return volatility_df.reindex(data.index).fillna(0)
