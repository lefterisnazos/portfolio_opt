import numpy as np
import pandas as pd
from .base import WeightAllocationModel
import datetime as dt


class RandomAllocation(WeightAllocationModel):


    def __init__(self, months_back):
        super(RandomAllocation, self).__init__()
        self.months_back = months_back

    def date_data_needed(self, date_from, date_to):

        return date_from - pd.DateOffset(months=self.months_back)

    def weights_allocate(self, date_from, date_to, ticker_list, data, **params):

        weights_list = []

        # care here date_from, date_to is oour whole period, start_date, and end_date is the subperiod for each rolled allocation
        for rebalance_date in pd.date_range(start=date_from, end=date_to, freq='MS'):

            # Define the period for calculating past performance (1 month before rebalance_date)
            start_date = rebalance_date - pd.DateOffset(months=1)
            end_date = rebalance_date - pd.DateOffset(days=1)

            # Slice the data for the past month
            past_month_data = data.loc[start_date:end_date, ticker_list]

            # Ensure there is data available
            if past_month_data.empty or len(past_month_data) < 2:
                # If not enough data, skip this rebalancing date
                continue

            # Calculate the returns over the past month for each ticker
            # Using the adjusted close prices
            initial_prices = past_month_data.iloc[0]
            final_prices = past_month_data.iloc[-1]
            returns = (final_prices - initial_prices) / initial_prices

            # Rank the tickers based on their returns (higher return gets rank 1)
            ranks = returns.rank(ascending=False, method='first')

            # Assign weights inversely proportional to ranks
            num_tickers = len(ticker_list)
            weight_values = (num_tickers - ranks + 1)

            # Normalize the weights to sum to 1
            weights = weight_values / weight_values.sum()

            # create a DF for the weights at this rebalance date
            weights_df = pd.DataFrame([weights.values], index=[rebalance_date], columns=ticker_list)

            weights_list.append(weights_df)

        weight_predictions = pd.concat(weights_list)

        weight_predictions = weight_predictions.sort_index()
        weight_predictions.columns = ticker_list


        return weight_predictions












