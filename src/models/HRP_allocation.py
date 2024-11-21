from .base import WeightAllocationModel
import pandas as pd
from .HRP_calculator import HRP_Calculator


# TODO: understand this functions and clean them up
class HRP(WeightAllocationModel):
    def __init__(self, months_back=3):
        super(HRP, self).__init__()
        self.months_back = months_back

    def date_data_needed(self, date_from, date_to):
        # Determine the historical data needed based on months_back parameter
        return date_from - pd.DateOffset(months=self.months_back)

    def weights_allocate(self, date_from, date_to, ticker_list, data, **params):
        weights_list = []

        # Iterate over each rebalance date within the specified date range - updation frequency 'MS'
        for rebalance_date in pd.date_range(start=date_from, end=date_to, freq='MS'):

            # define the past subperiod for calculating returns each time
            start_date = rebalance_date - pd.DateOffset(months=self.months_back)
            end_date = rebalance_date - pd.DateOffset(days=1)

            past_data = data.loc[start_date:end_date, ticker_list]

            if past_data.empty or len(past_data) < 2:
                # Skip this rebalance date if data is insufficient
                continue

            hrp_calculator = HRP_Calculator(past_data)
            hrp_weights = hrp_calculator.weights_allocate()

            weights_df = pd.DataFrame(data=[hrp_weights.values()], index=[rebalance_date], columns=hrp_weights.keys())
            weights_df =  weights_df[data.columns]
            weights_list.append(weights_df)

        # Concatenate all weights and sort by index (date)
        weight_predictions = pd.concat(weights_list)
        weight_predictions = weight_predictions.sort_index()
        #weight_predictions.columns = ticker_list

        return weight_predictions

    def __str__(self):
        return self.__class__.__name__






