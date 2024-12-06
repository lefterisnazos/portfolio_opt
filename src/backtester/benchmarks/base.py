from typing import List
from deepdiff import DeepHash
import pandas as pd
from typing import List
import yfinance as yf
import datetime as dt


class Benchmark:

    def __init__(self, name='Base_Benchmark', freq='M', starting_capital=10000000):
        self.name = name
        self.freq = freq
        self.starting_capital = starting_capital
        self.market_data = None

    def calculate(self, weight_predictions: pd.DataFrame, ticker_list: List, data: pd.DataFrame, market_data: pd.DataFrame, **kwargs):

        """
        This method is used to calculate the benchmark metric for the given data.

        Parameters
        ----------
        ticker_list: List[str]
            the list of tickers to fetch data for.
        weight_predictions: pd.DataFrame
            the predictions/weights from the Agent
        data: pd.DataFrame
            the whole period data from the backtester.
        market_data : pd.DataFrame
            sp500/our chosen's overall market data.
        ----------

        :return: case1) when we output 1 value-> a pd.Series for singular values with self.name as index, column name unnamed-dontcare (eg.in case we choose 'P' as frequency)
                 case2) when we want to output more than 1 value -> a pd.Dataframe or pd.Series with the correct indexing based on the groupby_freq staticmethod
        """
        pass

    def __hash__(self):
        return DeepHash(self)[self]

    #works with DatetimeIndex only
    @staticmethod
    def groupby_freq(dataframe, freq):

        """
        This method is used to group the data based on the frequency.

        Parameters
        ----------
        dataframe: pd.DataFrame
            the data to group.
        freq: str
            the frequency to group by.
        ----------
        Returns pd.DataFrameGroupBy
        """

        if freq == 'D':
            return dataframe.groupby([dataframe.index.date])
        elif freq == 'W':
            return dataframe.groupby([dataframe.index.year, dataframe.index.isocalendar().week])
        elif freq == 'M':
            return dataframe.groupby([dataframe.index.month])
        elif freq == 'Y':
            return dataframe.groupby([dataframe.index.year])
        elif freq == 'YM':
            return dataframe.groupby([dataframe.index.year, dataframe.index.month])
        elif freq == 'P':
            return dataframe

    # should be added for non linear metrics
    @staticmethod
    def to_frame_and_indexing(data, freq, name):
        """
        This method is used to convert the data to a DataFrame and index it based on the frequency.
        Parameters
        ----------
        data: pd.DataFrame or pd.Series or float or int
            the data to convert.
        freq: str
            the frequency to index by.
        name: str
            the name of the data.
        ----------
        Returns pd.DataFrame
        """
        
        if isinstance(data, pd.DataFrame):
            return data

        if freq == 'P':
            if isinstance(data, pd.Series):
                data.index = ['period']
                return data
            else:
                return pd.DataFrame({name: [data]}, index=['period'])
        return data







