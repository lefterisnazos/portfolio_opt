import os
import pandas as pd
import datetime
from typing import List


class WeightAllocationModel:

    ticker_list = None
    save = False

    def __init__(self):
        pass

    def weights_allocate(self, date_from: datetime.date, date_to: datetime.date, data: pd.DataFrame, ticker_list: List, **params):
        """
        :param data:  dataframe with all tickers for the whole period  (the result from DataProdiver object, but adjusted for date_data_needed)
        :param date_from: First day of predictions.
        :param date_to: Last day of predictions.
        :param: ticker_list
        :param params: Left empty, for future development.
        :return: returns Dataframe with dataframe, with amount of rows equal to the times we update weights.
                the index is the date we updated the dates. columns are the tickers. values the are the weights.
        """
        raise NotImplementedError('Every Model must implement its own predict function.')

    def __str__(self):
        """
        Returns models' name with the specified parameters to be used when extracting results.
        :return: str name of model
        """

        return "Weight-Allocation"

    def date_data_needed(self, date_from, date_to):
        """
        :param date_from: Starting day of the simulation
        :param date_to: Last day of the simulation
        :return: Returns the date that the model needs data from

        EG IF we lookback 2 months we will need 2 months back from our first date_from, so we will need to load 2 months more of data, besides our backtesting period
        """

        return NotImplementedError('Every model must implement its own date_data_needed method.')










