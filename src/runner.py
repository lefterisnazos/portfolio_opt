from random import Random
from agents.main import Agent
from backtester.main import Backtester
from datetime import date
import backtester.benchmarks.evaluation as b
from models.HRP_allocation import HRP
from models.HRP_sentiment_allocation import HRP_Sentiment
from models.other_models import EqualWeights, MarketCapWeights
from ticker_codes import tickers

# make sure to pip install -r requirements.txt

start_date = date(2024, 1, 1)
end_date = date(2024, 2, 29)

benchmarks = [b.PNL('P'),b.Sharpe('P'), b.PNL('YM'), b.Sharpe('YM')]

# agents = []
# months_back determines the amount of data used to make any prediction/weights_allocations
agents = [Agent(MarketCapWeights()), Agent(HRP_Sentiment(months_back=5, include_sentiment=True, async_getter=True))]

back_tester = Backtester(start_date=start_date,
                         end_date=end_date,
                         ticker_list= tickers,
                         benchmarks=benchmarks)

# Add the agents to the backcaster one by one.
for agent in agents:
    back_tester.add_agent(agent)

# run the backtester
back_tester.run_n_evaluate()

# Export the results to an excel file. Display parameter is for printing results to console as well.
back_tester.results_to_excel2(
    filename='backtesting_simulation_{}-{}.xlsx'.format(start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')),
    save_dir='results',
    disp=True
)

x=2
# call save once on exit, even if multiple files were created during the simulation.
