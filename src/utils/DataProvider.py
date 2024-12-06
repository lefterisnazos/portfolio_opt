import yfinance as yf
import pandas as pd
from typing import List
import datetime

class DataProvider:
    def __init__(self, start: datetime.date, end: datetime.date, tickers: List[str], target: str = "Adj Close") -> None:

        """
        Initialize the DataProvider with start and end dates as datetime.date objects, and a list of tickers.
        
        Parameters
        ----------
        start : datetime.date
            The start date of the data.
        end : datetime.date
            The end date of the data.   
        tickers : List[str]
            The list of tickers to fetch data for.
        target : str
            The target column to fetch data for. Default is "Adj Close".
        
        ----------
        """
        self.tickers = tickers
        self.start = start
        self.end = end
        self.data = pd.DataFrame()  # Initialize to empty
        self.target = target

    def provide(self) -> pd.DataFrame:
        """
        Fetches, cleans, and calculates returns for the given data.

        Parameters
        ----------
        None
        ----------
        Returns a pd.DataFrame of the cleaned and returns calculated data.
        """
        self.fetch()
        self.clean()
        self.calc_returns()
        return self.data[1:]

    def fetch(self) -> pd.DataFrame:
        """
        Fetches the data from Yahoo Finance API.
        Parameters
        ----------
        None
        ----------
        Returns a pd.DataFrame of the fetched data.
        """
        start_str = self.start.strftime('%Y-%m-%d')
        end_str = self.end.strftime('%Y-%m-%d')
        self.data = yf.download(self.tickers, start=start_str, end=end_str)
        self.data = self.data[self.target] if self.target else self.data
        self.data.index = self.data.index.tz_localize(None)

        return self.data

    def clean(self, brute = True) -> None:
        """
        Cleans the data by dropping columns with null values.
        Parameters
        ----------
        Brute : bool
            If True, the data will be cleaned by dropping all columns with null values.
        ----------
        Returns a boolean value indicating if the data was cleaned successfully.
        """
        if self.data.isnull().values.any():
            print("The dataset contains null or empty values")
            print("Pefroming cleaning")
            if brute:
                print("Here")
                self.data = self.data.dropna(axis = 1)
            else:  # TODO: the code below has not been tested
                missing_fractions = self.data.isnull().mean().sort_values(ascending=False)
                missing_fractions.head(10)
                drop_list = sorted(list(missing_fractions[missing_fractions > 0.3].index))
                self.data.drop(labels=drop_list, axis=1, inplace=True)
                # fill the missing values with the last value available in the dataset.
                self.data = self.data.fillna(method='ffill')
        else:
            print("The dataset contains no null values")
        return True

    def calc_returns(self):
        """
        Computes returns for the given data.

        Parameters
        ----------
        None
        ----------
        
        Returns pd.DataFrame with ticker returns.
        """
        self.data = self.data.pct_change()
        self.data = self.data.fillna(0)
