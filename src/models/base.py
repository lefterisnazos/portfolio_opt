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
        This method is used to predict the weights of the tickers for the given period.

        Parameters
        ----------
        data:  pd.DataFrame
            dataframe with all tickers for the whole period  (the result from DataProdiver object, but adjusted for date_data_needed)
        date_from: datetime
            First day of predictions.
        date_to: datetime
            Last day of predictions.
        ticker_list: List
            List of tickers to predict weights for.
        params: Left empty, for future development.
        ----------

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
        This method returns the date that the model needs data from to make predictions for the date_from.
        Parameters
        ----------
        date_from: datetime
            Starting day of the simulation
        date_to: 
            Last day of the simulation
        ----------    
        Return: Returns the date that the model needs data from

        EG IF we lookback 2 months we will need 2 months back from our first date_from, so we will need to load 2 months more of data, besides our backtesting period
        """

        return NotImplementedError('Every model must implement its own date_data_needed method.')










