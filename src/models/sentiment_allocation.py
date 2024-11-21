import numpy as np
import pandas as pd
from base import WeightAllocationModel

# TODO: understand this functions and clean them up
class Sentiment_Finbert(WeightAllocationModel):
    def __init__(self, months_back=1):
        super(Sentiment_Finbert, self).__init__()
        self.months_back = months_back

    def date_data_needed(self, date_from, date_to):

        return date_from - pd.DateOffset(months=self.months_back)

    def weights_allocate(self, date_from, date_to, data, ticker_list, **params):

        # for the current period a  final aggregated sentiment will be calculated for each ticker
        # we have created some helper functions below. For the time being we care about the abstract
        # This function will take as an extra parameter (**params) the current weights, calculated outside of this class (from hrp or something else)
        # if not we can naivly calculate the weights
        # It will return a dataframe with 1 row (index: corresponding re allocation date, values: new weights based on the 'allocation_method' function, columns:tickers
        pass

    def ticker_sentiment_analysis(self):

        pass

    def ticker_news_getter(self):

        pass

    def  allocation_method(self):

        pass