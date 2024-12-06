from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline
from transformers import DebertaTokenizer, DebertaForSequenceClassification
from requests.adapters import HTTPAdapter
import requests
from urllib3.util.retry import Retry
import aiohttp
import asyncio
from aiohttp import ClientSession
import os
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()
import nest_asyncio
nest_asyncio.apply()


class SentimentAnalyzer:

    """
    finbert is a bit slow evaluating the ticker news descriptions.
    for a given subperiod, The finbert model will evaluate number_of_stocks * amount of articles
    """
    def __init__(self, finbert=True):
        """
        Initialize the constructor with the finbert model and tokenizer.

        Parameters
        ----------
        finbert : bool
            Whether to use the finbert model or not. Default is True.
        ----------
        """
        self.api_key = 'LTLVSbi7rBjyjJtCpmLuTDPPhFsNSCyy'
        self.finbert_tokenizer, self.finbert_model, self.finbert_tokenizer = None, None, None

        if finbert:
            self.finbert_tokenizer = BertTokenizer.from_pretrained("yiyanghkust/finbert-tone")
            self.finbert_model = BertForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
            self.finbert_pipeline = pipeline(task="sentiment-analysis", model="yiyanghkust/finbert-tone", tokenizer=self.finbert_tokenizer)

    def fetch_ticker_news_with_retries(self, start_date, end_date, ticker):
        """
        Fetch news articles for a given ticker using the Polygon.io API with retries.

        Parameters
        ----------
        start_date : datetime.date
            The start date to fetch news articles.
        end_date : datetime.date    
            The end date to fetch news articles.    
        ticker : str    
            The ticker to fetch news articles for.
        ----------
        Returns a list of news articles for the given ticker.
        """
        url = "https://api.polygon.io/v2/reference/news"
        params = {'ticker': ticker,
                  'published_utc.gte': start_date.strftime('%Y-%m-%d'),
                  'published_utc.lte': end_date.strftime('%Y-%m-%d'),
                  'limit': 5,
                  'sort': 'published_utc',
                  'apiKey': self.api_key}

        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)

        try:
            response = session.get(url, params=params, timeout=20)
            response.raise_for_status()
            return response.json().get('results', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news for {ticker}: {e}")
            return []

    async def fetch_ticker_news_async(self, session: ClientSession, start_date, end_date, ticker):
        """
        Fetch news articles for a given ticker asynchronously using the Polygon.io API.

        Parameters
        ----------
        session : aiohttp.ClientSession
            The aiohttp client session to use for the request.
        start_date : datetime.date
            The start date to fetch news articles.
        end_date : datetime.date    
            The end date to fetch news articles.
        ticker : str
            The ticker to fetch news articles for.
        ----------
        Returns a list of news articles for the given ticker.
        """
        url = "https://api.polygon.io/v2/reference/news"
        params = {'ticker': ticker,
                  'published_utc.gte': start_date.strftime('%Y-%m-%d'),
                  'published_utc.lte': end_date.strftime('%Y-%m-%d'),
                  'limit': 5,
                  'sort': 'published_utc',
                  'apiKey': self.api_key}

        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with session.get(url, params=params, timeout=15) as response:
                    response.raise_for_status()
                    json_response = await response.json()
                    return json_response.get('results', [])
            except aiohttp.ClientError as e:
                print(f"Attempt {attempt + 1}/{max_retries}: Error fetching news for {ticker}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(4)
                else:
                    return []

    async def fetch_all_ticker_news(self, start_date, end_date, ticker_list):
        """
        Fetch news articles for all tickers asynchronously using the Polygon.io API.

        Parameters
        ----------
        start_date : datetime.date
            The start date to fetch news articles.
        end_date : datetime.date    
            The end date to fetch news articles.
        ticker : str
            The ticker to fetch news articles for.
        ----------
        Returns a list of news articles for the given ticker.
        """
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            tasks = [self.fetch_ticker_news_async(session, start_date, end_date, ticker) for ticker in ticker_list]
            return await asyncio.gather(*tasks)

    def calculate_sentiment(self, news_list):
        """
        Aggregate sentiment scores using the 'insights' key (Polygon.io) that has sentiment values for each article in the results/news_list

        Parameters
        ----------
        news_list : List[Dict]
            A list of news articles to calculate sentiment
        ----------
        Returns the aggregated sentiment score for the given news articles.
        """
        sentiment_scores = []
        for article in news_list:
            sentiment = article.get('insights', {})
            sentiment_score = (
                sentiment.get('positive', 0) -
                sentiment.get('negative', 0) +
                sentiment.get('neutral', 0) * 0.5  # adjust any factor as we may like
            )
            sentiment_scores.append(sentiment_score)

        return sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0

    def calculate_finbert_sentiment(self, news_list):
        """
        Calculate the aggregated sentiment using the FinBERT model for a list of news articles.

        Parameters
        ----------
        news_list : List[Dict]
            A list of news articles to calculate sentiment
        ----------
        Returns a dictionary of sentiment scores for the given news articles.
        """
        sentiment_scores = {"Positive": 0, "Negative": 0, "Neutral": 0}
        total_articles = len(news_list)

        for article in news_list:
            content = article.get('description')
            # if content is empty, ignore that article
            if content is None:
                total_articles -= 1
                continue

            # if article description content is more than 512 characters, it creates a problem for FinbErt. Thus we take up to the first 512 characters.
            truncated_content = content[:512]

            try:
                result = self.finbert_pipeline(truncated_content)
                sentiment = result[0]['label']
                score = result[0]['score']
                sentiment_scores[sentiment] += score
            except RuntimeError as re:
                print(f"Error processing article content for FinBERT: {re}")
                total_articles -= 1
                continue
            except Exception as e:
                print(f"Unexpected error during FinBERT sentiment analysis: {e}")
                total_articles -= 1
                continue

            # Normalize sentiment scores
        return sentiment_scores if total_articles > 0 else {"Positive": 0, "Negative": 0, "Neutral": 0}

    def calculate_finbert_aggregate_sentiment(self, sentiment_scores):
        """
        Calculate an overall sentiment score based on the FinBERT total scores of each class

        Parameters
        ----------
        sentiment_scores: Dict 
            Dictionary of sentiment scores. Values are the total scores for each of the pos,neg,neutral cases
        ----------
        sentiment_scores: Dictionary of sentiment scores. Values are the total scores for each of the pos,neg,neutral cases
        return: aggregated final sentiment score
        """
        total_score = sum(sentiment_scores.values())
        if total_score == 0:
            return 0

        weights = {"Positive": 1, "Neutral": 0, "Negative": -1}
        weighted_sum = sum(weights[sentiment] * (sentiment_scores[sentiment] / total_score) for sentiment in sentiment_scores)

        return weighted_sum
