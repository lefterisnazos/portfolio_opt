from .base import WeightAllocationModel#
import pandas as pd
from datetime import timedelta


class EqualWeights(WeightAllocationModel):

    def __init__(self):
        super().__init__()

    def date_data_needed(self, date_from, date_to):

        return date_from

    def weights_allocate(self, date_from, date_to, ticker_list, data, **params):
        """
        Allocates equal weights to all tickers for the specified date range.
        :param date_from: First day of predictions.
        :param date_to: Last day of predictions.
        :param data: DataFrame containing tickers and their data.
        :param ticker_list: List of tickers for which weights are to be calculated.
        :param params: Additional parameters (not used in this method).
        :return: DataFrame with dates as index, tickers as columns, and equal weights as values.
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

    def __str__(self):
        return self.__class__.__name__



