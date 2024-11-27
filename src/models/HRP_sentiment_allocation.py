import datetime

import urllib3
from .HRP_calculator import HRP_Calculator, HRP_Calculator_2, HRP_Calculator_3
import pandas as pd
from .base import WeightAllocationModel
import matplotlib.pyplot as plt
from models import plot_hrp_weights
from models import SentimentAnalyzer
import asyncio


class HRP_Sentiment(WeightAllocationModel):
    def __init__(self, months_back=3, include_sentiment=False, async_getter=True):
        super(HRP_Sentiment, self).__init__()
        self.months_back = months_back
        self.include_sentiment = include_sentiment
        self.async_getter = async_getter
        self.sentiment_analyzer = SentimentAnalyzer()

    def date_data_needed(self, date_from, date_to):
        return date_from - pd.DateOffset(months=self.months_back)

    def weights_allocate(self, date_from, date_to, ticker_list, data, **params):
        weights_list = []

        for rebalance_date in pd.date_range(start=date_from, end=date_to, freq='MS'):

            start_date = rebalance_date - pd.DateOffset(months=self.months_back)
            end_date = rebalance_date - pd.DateOffset(days=1)
            past_data = data.loc[start_date:end_date, ticker_list]

            if past_data.empty or len(past_data) < 2:
                continue

            hrp_calculator = HRP_Calculator_3(past_data)
            hrp_weights = hrp_calculator.weights_allocate()


            if self.include_sentiment is False:
                if isinstance(hrp_weights, pd.Series):
                    weights_data = [hrp_weights.values]
                else:
                    weights_data = [hrp_weights.values()]

                weights_df = pd.DataFrame(data=weights_data, index=[rebalance_date], columns=hrp_weights.keys())
                weights_df = weights_df[data.columns]

            else:
                weights_df = self.add_sentiment(start_date, end_date, data, hrp_weights, rebalance_date)

            weights_list.append(weights_df)

            plot_hrp_weights(hrp_weights, len(weights_list))

        weight_predictions = pd.concat(weights_list)
        weight_predictions = weight_predictions.sort_index()

        return weight_predictions


    def add_sentiment(self, start_date, end_date, ticker_list, hrp_weights: pd.Series, rebalance_date: datetime.date, **params):

        sentiment_scores = {}
        overall_sentiments = {}

        # if statement to get polygon data asynchronously or not
        if self.async_getter:
            news = asyncio.run(self.sentiment_analyzer.fetch_all_ticker_news(start_date, end_date, ticker_list))
            for ticker, news in zip(ticker_list, news):
                sentiment_scores[ticker] = self.sentiment_analyzer.calculate_finbert_sentiment(news)
                overall_sentiments[ticker] = self.sentiment_analyzer.calculate_finbert_aggregate_sentiment(sentiment_scores[ticker])
        else:
            for ticker in ticker_list:
                news = self.sentiment_analyzer.fetch_ticker_news_with_retries(start_date, end_date, ticker)
                sentiment_scores[ticker] = self.sentiment_analyzer.calculate_finbert_sentiment(news)
                overall_sentiments[ticker] = self.sentiment_analyzer.calculate_finbert_aggregate_sentiment(sentiment_scores[ticker])

        # think about the adjustment here. There is crazy bias. if we have small weights, but crazy sentiment, there won't be a difference
        adjusted_weights = {ticker: hrp_weights.get(ticker, 0) * (1 + overall_sentiments.get(ticker, 0)) for ticker in ticker_list}

        # normalize adjusted weights to sum to 1
        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:  # Avoid division by zero
            normalized_weights = {ticker: weight / total_weight for ticker, weight in adjusted_weights.items()}
        else:
            normalized_weights = {ticker: 0 for ticker in ticker_list}

        weights_df = pd.DataFrame(data=[normalized_weights.values()], index=[rebalance_date], columns=normalized_weights.keys())

        return weights_df