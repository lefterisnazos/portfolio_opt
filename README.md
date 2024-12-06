**Portfolio Optimization**

## Motivation

A backtesting infrastructure for comparing and evaluating different porfolio optimization strategies against benchmarks.

![image](https://github.com/user-attachments/assets/0ace29cf-3c79-4a00-baf9-547af86d04d6)


1) Backcasting requires agents that will participate in the simulation. In order for agents to participate in the simulation they need a prediction(Weight-Allocation) model, which is responsible for predicting the necessary values/weights.
2) The current implementation doesnt save the weights. It outputs the simulation results against the benchmarks we have decided we want to show.

* You can add benchmarks in the runner.py as follows: benchmarks = [b.PNL('P'),b.Sharpe('P')] denoting, the metric and its frequency.
* You can add Agents, that inherit a model, and backtest them with the Backtester Class.

* run src/runner.py. For runner to run, you need to have a polygon_apikey (subscription based)

## Models Implemented



## SETUP

*pip install -r requirements.txt*

