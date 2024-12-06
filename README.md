**Portfolio Optimization**

## Motivation

A backtesting infrastructure for comparing and evaluating different porfolio optimization strategies against benchmarks.  (python 3.9.10)

![image](https://github.com/user-attachments/assets/4dd2dad7-70af-44b6-a34b-7147686b8f4b)


1) Backcasting requires agents that will participate in the simulation. In order for agents to participate in the simulation they need a prediction(Weight-Allocation) model, which is responsible for predicting the necessary values/weights.
2) The current implementation doesnt save the weights. It outputs the simulation results against the benchmarks we have decided we want to show.

* You can add benchmarks in the runner.py as follows: benchmarks = [b.PNL('P'),b.Sharpe('P')] denoting, the metric and its frequency
* You add Agents, that inherit a model, and backtest them with the Backtester Class.

* For runner to run, you need to have a polygon_apikey (subscription based). The tickers list and api_key are found in the ticker_codes.py file
  
* run src/runner.py.  

## Models Implemented

* HRP based on Lopez De Prados implementation
* HRP + News_Sentiment:
     - HRP + ticker news sentiment utilizing a pretrained financial BERT model (tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone'), and polygon.io api for getting articles for tickers for given timestamps.
     - News Data getters are implemented asynchronously. 
* Benchmark Models:
   - Market Cap Weighted Portfolio
   - Equal Weighted Portfolio
     
## Evaluation Metrics Implemented
* PNL
* Sharpe
* Beta
* CAPM Adjusted Market Porftolio, for a beta adjusted comparison with the market
* Information Ratio

 Metrics like Sharpe and Information Ratio are reported in an annualized basis.

## SETUP

*pip install -r requirements.txt*

