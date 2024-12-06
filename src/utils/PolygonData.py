import aiohttp
import asyncio
import pandas as pd
import requests
import datetime
from ticker_codes import polygon_api_key
import nest_asyncio
nest_asyncio.apply()


class MarketCapFetcher:
    def __init__(self):
        """
        Initialize the MarketCapFetcher with the Polygon.io API key.
        
        Parameters
        ----------
        None
        ----------
        """
        self.polygon_api_key = polygon_api_key

    def get_next_trading_day(self, date):
        """
        Check if the given date is a valid trading day.
        Here we use a random ticker like 'AAPL' to check if the 'date' has been a valid trading day.
        
        Parameters
        ----------
        date : datetime.date
            The date to check if it is a valid trading day.
        ----------
        Returbn: date if it is a valid trading day or next available trading day.
        """
        
        k=0
        while True:
            url = f'https://api.polygon.io/v1/open-close/AAPL/{date.strftime("%Y-%m-%d")}'
            params = {"apiKey": self.polygon_api_key}

            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                result = response.json()

                if result['status'] == "OK":
                    return date.strftime("%Y-%m-%d")

                date = date + datetime.timedelta(days=1)

            except requests.exceptions.RequestException as e:
                print(f"Error checking trading day: {e}")
                date += datetime.timedelta(days=1)
                k=k+1
                if k>3:
                    break

    async def fetch_price_data_async(self, session: aiohttp.ClientSession, ticker, date):
        """
        Fetch historical price data for a specific date asynchronously using Polygon.io.
        
        Parameters
        ----------
        session : aiohttp.ClientSession
            The aiohttp client session to use for the request.
        ticker : str
            The ticker to fetch price data for.
        date : str
            The date to fetch price data for.
        ----------
        Returns the closing price for the given ticker on the given date.
        
        """
        url = f"https://api.polygon.io/v1/open-close/{ticker}/{date}"
        params = {"apiKey": self.polygon_api_key}

        try:
            async with session.get(url, params=params, timeout=30) as response:
                response.raise_for_status()
                json_response = await response.json()
                if "close" in json_response:
                    return json_response["close"]
                else:
                    print(f"No price data available for {ticker} on {date}")
                    return None
        except aiohttp.ClientError as e:
            print(f"Error fetching price data for {ticker} on {date}: {e}")
            return None

    async def fetch_shares_outstanding_async(self, session: aiohttp.ClientSession, ticker):
        """
        Fetch shares outstanding for a ticker asynchronously using Polygon.io.
        
        Parameters
        ----------
        session : aiohttp.ClientSession
            The aiohttp client session to use for the request.
        ticker : str
            The ticker to fetch shares outstanding for.
        ----------
        Returns the shares outstanding for the given ticker.
        """
        url = f"https://api.polygon.io/v3/reference/tickers/{ticker}"
        params = {"apiKey": self.polygon_api_key}

        try:
            async with session.get(url, params=params, timeout=30) as response:
                response.raise_for_status()
                json_response = await response.json()
                if "results" in json_response and "share_class_shares_outstanding" in json_response["results"]:
                    return json_response["results"]["share_class_shares_outstanding"]
                else:
                    print(f"No shares outstanding data available for {ticker}")
                    return None
        except aiohttp.ClientError as e:
            print(f"Error fetching shares outstanding for {ticker}: {e}")
            return None

    async def fetch_market_cap_for_ticker(self, session: aiohttp.ClientSession, ticker, date):
        """
        Fetch price data and shares outstanding asynchronously for a specific date,
        and calculate market cap for a ticker.

        Parameters
        ----------
        session : aiohttp.ClientSession
            The aiohttp client session to use for the request.
        ticker : str
            The ticker to fetch market cap for.
        date : str 
            The date to fetch market cap for.
        ----------
        Returns a dictionary with the date, ticker, and market cap.
        """
        close_price = await self.fetch_price_data_async(session, ticker, date)
        shares_outstanding = await self.fetch_shares_outstanding_async(session, ticker)

        if close_price is not None and shares_outstanding is not None:
            market_cap = close_price * shares_outstanding
            return {"date": date, "ticker": ticker, "market_cap": market_cap}
        else:
            return {"date": date, "ticker": ticker, "market_cap": None}

