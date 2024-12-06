from agents import WeightAllocationModel

class Agent:

    def __init__(self, model: WeightAllocationModel):
        """
        Constructor of the Agent class.

        Parameters
        ----------
        model : WeightAllocationModel
            The model to allocate weights.
        ----------
        Returns none
        """

        self.model = model
        self.ticker_list = None
        self.weight_predictions = None

    def weights_allocate(self, from_date, to_date, ticker_list, data):
        """
        This method is used to allocate weights for the given data.
        
        Paramters
        ----------
        from_date : datetime.date
            The start date of the simulation.
        to_date : datetime.date
            The end date of the simulation.
        ticker_list : List[str]
            The list of tickers to fetch data for.
        data : pd.DataFrame
            The whole period data from the backtester.
        ----------
        Returns none
        """

        WeightAllocationModel.ticker_list =  self.ticker_list

        self.weight_predictions = self.model.weights_allocate(from_date, to_date, ticker_list, data)

        # adjusting weight_prediction frequency and indexing to our data.
        self.weight_predictions = self.weight_predictions.resample('D').ffill().dropna(how='all')
        self.weight_predictions = self.weight_predictions.reindex(data.index).ffill().fillna(0)
        self.weight_predictions = self.weight_predictions[(self.weight_predictions.index.date>=from_date) & (self.weight_predictions.index.date<=to_date)]

    def date_data_needed(self, date_from, date_to=None):
        return self.model.date_data_needed(date_from, date_to)

    def __str__(self):
        return "Agent with weights allocation model: {}".format(str(self.model))

    def __hash__(self):
        return f"{str(self.model)}".__hash__()

    def sheet_name(self):
        return f"{str(self.model)}"