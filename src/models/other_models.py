from .base import WeightAllocationModel#
import pandas as pd
from datetime import timedelta
import datetime
from models import MarketCapFetcher
import aiohttp
import asyncio
import os
import certifi
import nest_asyncio
nest_asyncio.apply()
os.environ['SSL_CERT_FILE'] = certifi.where()


class EqualWeights(WeightAllocationModel):

    def __init__(self):
        """
        Constructor of the EqualWeights class.

        Parameters
        ----------
        None
        ----------
        """
        super(EqualWeights, self).__init__()

    def date_data_needed(self, date_from, date_to):

        return date_from

    def __str__(self):
        return self.__class__.__name__

    def __hash__(self):
        return self.__class__.__name__.__hash__()

    def weights_allocate(self, date_from, date_to, ticker_list, data, **params):
        """
        Allocates equal weights to all tickers for the specified date range.

        Parameters
        ----------
        date_from: datetime
            First day of predictions.
        date_to: datetime
            Last day of predictions.
        data: pd.DataFrame
            DataFrame containing tickers and their data.
        ticker_list: List
            List of tickers for which weights are to be calculated.
        params: 
            Additional parameters (not used in this method).
        ----------
        
        Return: DataFrame with dates as index, tickers as columns, and equal weights as values.
        """

        rebalancing_dates = pd.date_range(start=date_from, end=date_to, freq='D')

        num_tickers = len(ticker_list)

        equal_weight = 1 / num_tickers

        # Create a DataFrame for weights
        weights = pd.DataFrame(
            data=[[equal_weight] * num_tickers for _ in range(len(rebalancing_dates))],
            index = rebalancing_dates,
            columns=ticker_list
        )

        return weights


class MarketCapWeights(WeightAllocationModel):

    def __init__(self):
        super(MarketCapWeights, self).__init__()
        self.MarketCapFetcher = MarketCapFetcher()

    def date_data_needed(self, date_from, date_to):

        return date_from

    def __str__(self):
        return self.__class__.__name__

    def __hash__(self):
        return self.__class__.__name__.__hash__()

    async def calculate_market_cap(self, date, ticker_list):
        """
        Calculate market capitalization asynchronously for multiple tickers on a specific date.

        Parameters
        ----------
        date: datetime
            The date for which to calculate market cap.
        
        ticker_list: List
            List of tickers to calculate market cap for.
        ----------
        Returns:
            pd.DataFrame: DataFrame of market capitalization for each ticker and the given date.
        """

        trading_day = self.MarketCapFetcher.get_next_trading_day(date)

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            tasks = [self.MarketCapFetcher.fetch_market_cap_for_ticker(session, ticker, trading_day) for ticker in ticker_list]
            results = await asyncio.gather(*tasks)

        # Combine results into a single DataFrame
        market_cap_data = pd.DataFrame(results)
        market_cap_data = market_cap_data.pivot(index="date", columns="ticker", values="market_cap")
        return market_cap_data

    def weights_allocate(self, date_from, date_to, ticker_list, data, **params):
        """
        Allocate weights based on market capitalization.
        Parameters
        ----------
        date_from: datetime
            First day of predictions.
        date_to: datetime
            Last day of predictions.
        data: pd.DataFrame
            DataFrame containing tickers and their data
        ticker_list: List
            List of tickers to predict weights for.
        ----------
        Returns: A DataFrame of weights for each rebalance date.
        """
        weights_list = []

        for rebalance_date in pd.date_range(start=date_from, end=date_to, freq="MS"):

            # Fetch market cap data for the rebalance date

            market_cap_data = asyncio.run(self.calculate_market_cap(rebalance_date, ticker_list))
            market_cap_data.index = [rebalance_date]

            if market_cap_data.empty or market_cap_data.iloc[0].sum() == 0:
                print(f"Skipping {rebalance_date} due to insufficient market cap data.")
                continue

            # Calculate weights proportional to market capitalization
            weights = market_cap_data.div(market_cap_data.sum(axis=1), axis=0)

            weights_list.append(weights)

        # Combine all weights into a single DataFrame
        weight_predictions = pd.concat(weights_list)
        return weight_predictions




