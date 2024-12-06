from backtester.benchmarks.base import Benchmark
import pandas as pd
import numpy as np



class PNL(Benchmark):

    """"
    First 3 lines of calculate function should be implemented in every calculation function, in order to be able to compare weight_allocations and daily_returns
    """
    def __init__(self, freq='D'):
        super(PNL, self).__init__(name="PNL (%)", freq=freq)


    def calculate(self, weight_predictions, ticker_list, data, market_data, **kwargs):

        """
        EJ lecture: log(1+x) = x approximately, for small x. SO if we use cumsum() on returns we approximate the cumulative return
        more precisely: log(total_ret) = log((1+r1)*(1+r2)*...*(1_r_n)) = log(1+r1) + log(1+r2) + ... + log(1+r_n) = r1 + r2 + rn returns
        Parameters
        ----------
        weight_predictions: pd.DataFrame
            the predictions/weights from the Agent  
        data: pd.DataFrame
            the whole period data from the backtester.
        freq: str
            the frequency to group by.
        ----------
        Returns pd.DataFrame
        """

        portfolio_returns = (weight_predictions * data).sum(axis=1)
        # portfolio_returns_cumsum = portfolio_pnl.cumsum()
        portfolio_returns_df = portfolio_returns.to_frame(name=self.name)

        grouped_pnl = self.groupby_freq(portfolio_returns_df, self.freq).sum()*100
        grouped_pnl = self.to_frame_and_indexing(grouped_pnl, self.freq, self.name)

        return (grouped_pnl)

class Sharpe(Benchmark):
    """
    Report sharpe ratio for any period/frequence in an annualized basis
    
    """

    def __init__(self, freq='D', risk_free_rate=0):

        """
        Constructor for the Sharpe ratio calculation.
        
        Parameters
        ----------
        freq: str
            the frequency to group by.
        risk_free_rate: float
            the risk-free rate to use in the calculation.
        ----------
        Returns None
        """
        super(Sharpe, self).__init__(name="Sharpe", freq=freq)
        self.risk_free_rate = risk_free_rate

    def calculate(self, weight_predictions, ticker_list, data, market_data, **kwargs):
        """
        Calculate the Sharpe ratio of the portfolio.

        Parameters
        ----------
        weight_predictions: pd.DataFrame
            the predictions/weights from the Agent  
        data: pd.DataFrame
            the whole period data from the backtester.
        freq: str
            the frequency to group by.
        ----------
        Returns pd.DataFrame
        """

        # Risk-free rate calculation
        riskfree_rates = market_data[['^IRX']] / 252

        # Portfolio returns calculation
        portfolio_returns = (weight_predictions * data).sum(axis=1)

        # Excess returns calculation
        excess_returns = portfolio_returns - riskfree_rates.values.flatten()

        # Group excess returns and portfolio returns by the specified frequency
        grouped_excess_returns = self.groupby_freq(excess_returns, self.freq)
        grouped_portfolio_returns = self.groupby_freq(portfolio_returns, self.freq)

        if self.freq == "P":
            excess_mean_return = grouped_excess_returns.mean()
            portfolio_std = grouped_portfolio_returns.std()
            sharpe_ratio_df = (excess_mean_return / portfolio_std) * np.sqrt(252)
        else:
            # Apply calculation for each group
            sharpe_ratio = grouped_excess_returns.apply(lambda x: (x.mean() / portfolio_returns.std()) * np.sqrt(252) if x.std() != 0 else 0)

            sharpe_ratio_df = sharpe_ratio.to_frame(name=self.name)

        sharpe_ratio_df = self.to_frame_and_indexing(sharpe_ratio_df, self.freq, self.name)

        sharpe_ratio_df = sharpe_ratio_df.replace([float('inf'), float('-inf')], 0).fillna(0)

        return sharpe_ratio_df


class Beta(Benchmark):

    def __init__(self, freq='P'):

        """
        Constructor for the Beta calculation.
        
        Parameters
        ----------
        freq: str
            the frequency to group by.
            
        ----------
        Returns None
        """

        super(Beta, self).__init__(name="Beta", freq=freq)
        self.sp500_returns = None
        if self.freq == 'D':
            raise ValueError('D is not an acceptable frequency. We cant calculate daily beta, with daily data')

    def calculate(self, weight_predictions, ticker_list, data, market_data, **kwargs):
        """
        Calculate beta of the portfolio compared to the market benchmark.

        Parameters
        ----------
        weight_predictions: pd.DataFrame
            the predictions/weights from the Agent
        ticker_list: List[str]
            the list of tickers to fetch data for.
        data: pd.DataFrame
            the whole period data from the backtester.
        freq: str
            the frequency to group by.
        ----------
        Returns pd.DataFrame
        """
        #choose sp500 returns from market_data
        market = market_data[['^GSPC']]
        # Calculate portfolio returns

        pnl = PNL(freq='D')
        returns = pnl.calculate(weight_predictions, ticker_list, data, market)/100
        returns.index = pd.DatetimeIndex(returns.index)

        returns.rename(columns={returns.columns[0]: "our_returns"}, inplace=True)
        market.rename(columns={market.columns[0]: "market_returns"}, inplace=True)

        #convert to pd.Series
        returns = returns.squeeze()
        market= market.squeeze()

        grouped_portfolio = self.groupby_freq(returns, self.freq)
        grouped_market = self.groupby_freq(market, self.freq)

        def beta_for_group(portfolio_group, market_group):
            covariance = portfolio_group.cov(market_group)
            market_variance = market_group.var()
            return covariance / market_variance if market_variance != 0 else 0

        beta_values = {}
        if self.freq !='P':
            for group_key in grouped_portfolio.groups.keys():
                portfolio_group = grouped_portfolio.get_group(group_key)
                market_group = grouped_market.get_group(group_key)
                beta = beta_for_group(portfolio_group, market_group)
                beta_values[group_key] = beta
        else:
            beta_values['period'] = beta_for_group(grouped_portfolio, grouped_market)

        # Convert beta values to a DataFrame with grouping index
        beta_df = pd.DataFrame.from_dict(beta_values, orient="index", columns=[self.name])
        beta_df = self.to_frame_and_indexing(beta_df, self.freq, self.name)
        return beta_df


class CAPM_Adjusted_Market_Portfolio(Benchmark):
    def __init__(self, freq='D', beta_model=0.5):
        """
        Constructor for the CAPM adjusted portfolio calculation.

        Parameters
        ----------
        freq: str
            the frequency to group by.
        beta_model: float
            the beta value to use in the calculation.
        ----------
        Returns None
        """
        super(CAPM_Adjusted_Market_Portfolio, self).__init__(name="CAPM_Adjusted_Market_Portfolio", freq=freq)
        self.beta = None
        if self.freq == 'D' or self.freq == 'W':
            raise ValueError('CAPM analysis not support for D or W frequency')

    def calculate(self, weight_predictions, ticker_list, data, market_data, **kwargs):
        """
        Calculate portfolio PnL and compare it to a benchmark of beta*SP500 + beta*Cash.

        Parameters
        ----------
        weight_predictions: pd.DataFrame
            the predictions/weights from the Agent
        ticker_list: List[str]
            the list of tickers to fetch data for.
        data: pd.DataFrame
            the whole period data from the backtester.
        market_data: pd.DataFrame  
            dataframde of the market data with the SP500 and the risk-free rate.
        ----------
        """
        # Extract risk-free rate series
        riskfree_rates = market_data[['^IRX']]/252
        market = market_data[['^GSPC']]

        self.beta = Beta('YM').calculate(weight_predictions, ticker_list, data, market)
        self.beta.index = pd.to_datetime(data.index.to_period('M').unique().to_timestamp())
        self.beta = self.beta.reindex(data.index, method='ffill')

        # Calculate portfolio returns
        pnl = PNL(freq='D')
        portfolio_returns = pnl.calculate(weight_predictions, ticker_list, data, market_data) / 100
        portfolio_returns.index = pd.DatetimeIndex(portfolio_returns.index)

        # benchmark returns: eg: 0.5*SP500 + 0.5*Cash, where 0.5=beta
        benchmark_pnl = (
            self.beta.values * market+
            (1 - self.beta.values) * riskfree_rates.values  # Daily risk-free rate
        )

        grouped_benchmark_pnl = self.groupby_freq(benchmark_pnl, self.freq).sum() * 100
        grouped_benchmark_pnl = self.to_frame_and_indexing(grouped_benchmark_pnl, self.freq, self.name)

        return grouped_benchmark_pnl


class InformationRatio(Benchmark):
    def __init__(self, freq='D'):
        """
        Constructor for the Information Ratio calculation.

        Parameters
        ----------
        freq: str
            the frequency to group by.
        ----------
        Returns None
        """
        super(InformationRatio, self).__init__(name="InformationRatio", freq=freq)

    def calculate(self, weight_predictions, ticker_list, data, market_data, **kwargs):
        """
        Calculate the information ratio of the portfolio compared to the market benchmark.

        Parameters
        ----------
        weight_predictions: pd.DataFrame
            the predictions/weights from the Agent
        ticker_list: List[str]
            the list of tickers to fetch data for.
        data: pd.DataFrame
            the whole period data from the backtester.
        market_data: pd.DataFrame
            dataframde of the market data with the SP500 and the risk-free rate.
        """

        market = market_data[['^GSPC']]

        pnl = PNL(freq='D')
        returns = pnl.calculate(weight_predictions, ticker_list, data, market) / 100
        returns.index = pd.DatetimeIndex(returns.index)

        returns.rename(columns={returns.columns[0]: "our_returns"}, inplace=True)
        market.rename(columns={market.columns[0]: "market_returns"}, inplace=True)

        excess_returns =  returns['our_returns'] - market['market_returns']
        grouped_excess_returns = self.groupby_freq(excess_returns, self.freq)

        if self.freq == 'P':
            information_ratio_df = ((grouped_excess_returns.mean()) / (grouped_excess_returns.std())) * np.sqrt(252)
        else:
            information_ratio = grouped_excess_returns.apply(
                lambda x: (x.mean() / x.std()) *np.sqrt(252) if x.std() !=0 else 0)

            information_ratio_df = information_ratio.to_frame(name=self.name)

        information_ratio_df = self.to_frame_and_indexing(information_ratio_df, self.freq, self.name)

        return information_ratio_df
