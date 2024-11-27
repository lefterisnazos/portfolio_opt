from .base import WeightAllocationModel
import pandas as pd
from .HRP_calculator import HRP_Calculator, HRP_Calculator_2, HRP_Calculator_3
from models import plot_hrp_weights


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

            past_data = data.loc[start_date:end_date, list(data.columns)]

            if past_data.empty or len(past_data) < 2:
                # Skip this rebalance date if data is insufficient
                continue

            hrp_calculator = HRP_Calculator_3(past_data)
            hrp_weights = hrp_calculator.weights_allocate()

            if isinstance(hrp_weights, pd.Series):
                weights_data = [hrp_weights.values]
            else:
                weights_data = [hrp_weights.values()]

            weights_df = pd.DataFrame(data=weights_data, index=[rebalance_date], columns=hrp_weights.keys())
            weights_df =  weights_df[data.columns]
            weights_list.append(weights_df)

            plot_hrp_weights(hrp_weights, len(weights_list))

        # Concatenate all weights and sort by index (date)
        weight_predictions = pd.concat(weights_list)
        weight_predictions = weight_predictions.sort_index()
        #weight_predictions.columns = ticker_list

        return weight_predictions






