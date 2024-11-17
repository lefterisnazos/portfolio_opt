import numpy as np
import pandas as pd
from base import WeightAllocationModel
from  HRP_allocation import HRP
from sentiment_allocation import Sentiment_Finbert

# TODO: understand this functions and clean them up
class Bandito_Model(WeightAllocationModel):
    def __init__(self, model1: WeightAllocationModel, model2: Sentiment_Finbert, months_back=3):
        super(Bandito_Model, self).__init__()
        self.model1= model1
        self.model2 = model2 # indicating that specifically the Sentiment_Finbert will be called here, and not a generic WeightAllocationModel. Not necessary to be honest; we will see
        self.months_back = months_back

    def date_data_needed(self, date_from, date_to):

        return date_from - pd.DateOffset(months=self.months_back)

    def weights_allocate(self, date_from, date_to, data, ticker_list, **params):

        # calculate in a rolling basis the weights, by calculating hrp and the sentiment second in a loop
        # by nature, the sentiment has to have as an extra input current weights, so its structure will be different from hrp abstract


        pass