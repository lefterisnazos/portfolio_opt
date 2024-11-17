import numpy as np
import pandas as pd
from .base import WeightAllocationModel
import riskfolio as rp


# TODO: understand this functions and clean them up
class HRP(WeightAllocationModel):
    def __init__(self, months_back=3):
        super(HRP, self).__init__()
        self.months_back = months_back

    def date_data_needed(self, date_from, date_to):
        # Determine the historical data needed based on months_back parameter
        return date_from - pd.DateOffset(months=self.months_back)

    def calculate_hrp_weights(self, returns):
        port = rp.HCPortfolio(returns=returns)

        model = 'HRP'  # Could be HRP or HERC
        codependence = 'pearson'  # Correlation matrix used to group assets in clusters
        rm = 'MV'  # Risk measure used, this time will be variance
        rf = 0  # Risk free rate
        linkage = 'single'  # Linkage method used to build clusters
        max_k = 10  # Max number of clusters used in two difference gap statistic, only for HERC model
        leaf_order = True  # Consider optimal order of leafs in dendrogram

        weights = port.optimization(model=model, codependence=codependence, rm=rm, rf=rf, linkage=linkage, max_k=max_k, leaf_order=leaf_order)

        return weights

    def weights_allocate(self, date_from, date_to, ticker_list, data, **params):
        weights_list = []

        # Iterate over each rebalance date within the specified date range - updation frequency 'MS'
        for rebalance_date in pd.date_range(start=date_from, end=date_to, freq='MS'):

            # define the past subperiod for calculating returns each time
            start_date = rebalance_date - pd.DateOffset(months=self.months_back)
            end_date = rebalance_date - pd.DateOffset(days=1)

            past_data = data.loc[start_date:end_date, ticker_list]

            # Ensure there's enough data
            if past_data.empty or len(past_data) < 2:
                # Skip this rebalance date if data is insufficient
                continue

            # Calculate returns for the historical period
            returns = past_data.pct_change().dropna()

            # Calculate HRP weights
            hrp_weights = self.calculate_hrp_weights(returns)
            hrp_weights = np.array(hrp_weights).reshape(1, len(ticker_list))

            weights_df = pd.DataFrame(data=hrp_weights, index=[rebalance_date], columns=ticker_list)

            weights_list.append(weights_df)

        # Concatenate all weights and sort by index (date)
        weight_predictions = pd.concat(weights_list)
        weight_predictions = weight_predictions.sort_index()
        weight_predictions.columns = ticker_list

        return weight_predictions
