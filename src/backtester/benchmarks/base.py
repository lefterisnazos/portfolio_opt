from deepdiff import DeepHash
import pandas as pd


class Benchmark:

    def __init__(self, name='Base_Benchmark', freq='M', starting_capital=10000000):
        self.name = name
        self.freq = freq
        self.starting_capital = starting_capital

    def calculate(self, weight_predictions, ticker_list, data, **kwargs):

        """
        :param weight_predictions: the predictions/weights from the Agent
        :param data: the whole period data from the backtester.
        :return: case1)c when we output 1 value-> a pd.Series for singular values with self.name as index, column name unnamed-dontcare (eg.in case we choose 'P' as frequency)
                 case2) when we want to output more than 1 value -> a pd.Dataframe with the correct indexing based on the groupby_freq staticmethod and self.name as the column name
        """
        pass


    def __hash__(self):
        return DeepHash(self)[self]

    @staticmethod
    def groupby_freq(dataframe, freq):
        if freq == 'D':
            return dataframe.groupby([dataframe.index.date])
        elif freq == 'W':
            return dataframe.groupby([dataframe.index.year, dataframe.index.isocalendar().week])
        elif freq == 'M':
            return dataframe.groupby([dataframe.index.month])
        elif freq == 'Y':
            return dataframe.groupby([dataframe.index.year])
        elif freq == 'YM':
            return dataframe.groupby([dataframe.index.year, dataframe.index.month])
        elif freq == 'P':
            return dataframe

    @staticmethod
    def to_frame_and_indexing(data, freq, name):
        if freq == 'P':
            if isinstance(data, pd.Series):
                dataframe = data
                dataframe.index = ['period']
            else:
                dataframe = pd.Series([data], index=['period'], name=name)
        else:
            dataframe = data.to_frame(name=name)
        return dataframe


