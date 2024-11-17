import pandas as pd
import yfinance as yf
from typing import List
import datetime
from .ticker_codes import etf_ticker_universe


class DataProvider:
    def __init__(self, start: datetime.date, end: datetime.date, tickers: List[str], target: str = "Adj Close") -> None:
        """
        Initialize the DataProvider with start and end dates as datetime.date objects, and a list of tickers.
        """
        self.tickers = tickers
        self.start = start
        self.end = end
        self.data = pd.DataFrame()  # Initialize to empty
        self.target = target

    def fetch(self) -> pd.DataFrame:
        start_str = self.start.strftime('%Y-%m-%d')
        end_str = self.end.strftime('%Y-%m-%d')
        self.data = yf.download(self.tickers, start=start_str, end=end_str)
        self.data = self.data[self.target] if self.target else self.data
        self.data.index = self.data.index.tz_localize(None)

        return self.data

    def clean(self, brute = True) -> None:
        """
        Clean up the data
        """
        if self.data.isnull().values.any():
            print("The dataset contains null or empty values")
            print("Pefroming cleaning")
            if brute:
                self.data = self.data.dropna()
            else: # TODO: the code below has not been tested
                missing_fractions = self.data.isnull().mean().sort_values(ascending=False)
                missing_fractions.head(10)
                drop_list = sorted(list(missing_fractions[missing_fractions > 0.3].index))
                self.data.drop(labels=drop_list, axis=1, inplace=True)
                # fill the missing values with the last value available in the dataset.
                self.data = self.data.fillna(method='ffill')
        else:
            print("The dataset contains no null values")
        return True

    @staticmethod
    def load_etf_stock_data(etf_list, start_date=None, end_date=None, etf_ticker_map=etf_ticker_universe):
        """
        Loads adjusted close, adjusted high, adjusted low, and volume data for each stock in the selected ETFs.

        Parameters:
        - etf_list: List of ETF sector symbols (e.g., ['xlf', 'xli'])
        - start_date: Start date for the data in 'YYYY-MM-DD' format (optional)
        - end_date: End date for the data in 'YYYY-MM-DD' format (optional)
        - etf_ticker map: Dict with str as key, lists as values

        Returns:
        - etf_data_dict: Nested dictionary with ETF sectors as keys, and dictionaries with ticker names as keys and stock data as values.
        """
        etf_data_dict = {}

        for etf in etf_list:
            etf_lower = etf.lower()
            etf_upper = etf.upper()
            if etf_lower not in etf_ticker_map:
                print(f"ETF '{etf_upper}' not recognized.")
                continue

            tickers = etf_ticker_map[etf_lower]
            print(f"Downloading data for ETF '{etf_upper}' with tickers: {tickers}")

            etf_ticker_data = {}

            for ticker in tickers:
                # Download data for the ticker individually
                try:
                    ticker_obj = yf.Ticker(ticker)
                    data = ticker_obj.history(start=start_date, end=end_date, auto_adjust=True)

                    if data.empty:
                        print(f"No data retrieved for ticker '{ticker}' in ETF '{etf_upper}'.")
                        continue

                    selected_columns = ['High', 'Low', 'Close', 'Volume']
                    ticker_data = data[selected_columns]

                    # Store the data in the nested dictionary
                    etf_ticker_data[ticker] = ticker_data

                except Exception as e:
                    print(f"Error retrieving data for ticker '{ticker}' in ETF '{etf_upper}': {e}")
                    continue

            etf_data_dict[etf_lower] = etf_ticker_data

        return etf_data_dict