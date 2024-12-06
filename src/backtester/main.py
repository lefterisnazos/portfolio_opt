import pandas as pd
from agents.main import Agent
import copy
from utils.DataProvider import DataProvider
import os
from backtester import WeightAllocationModel

class Backtester:

    def __init__(self,start_date, end_date, ticker_list, benchmarks, market_tickers, save=False):
        """
        Constructor of the Backtester class.
        
        Parameters
        ----------
        start_date : datetime.date
            The start date of the simulation.   
        end_date : datetime.date
            The end date of the simulation.
        ticker_list : List[str]
            The list of tickers to fetch data for.
        benchmarks : List[Benchmark]
            The list of benchmarks to evaluate the agents.
        market_tickers : List[str]
            The list of market tickers to fetch data for.
        save : bool
            The boolean value to save the simulation results.
        ----------
        """
        self.start_date = start_date
        self.end_date = end_date
        self.tickers = sorted(ticker_list)
        self.market_tickers = market_tickers
        self.benchmarks = benchmarks

        self.data_from = None
        self.data = None
        self.market = None

        self.agents = []
        self.new_agents = []
        self.changed_agents = []
        self.benchmarks = benchmarks
        self.results = {}
        self.excel_writer = None

        self.save = save
        WeightAllocationModel.save = save

    def data_date_from(self):

        """
        This method is used to find the earliest date that the agents need data from.
        
        Parameters
        ----------
        None
        ----------
        Returns datetime of date_from
        """

        date_from = self.start_date
        for agent in self.agents:
            temp = agent.date_data_needed(self.start_date, self.end_date)
            if pd.Timestamp(temp) < pd.Timestamp(date_from):
                date_from = temp

        return date_from

    def get_data(self):
        """
        This method is used to fetch the data from the data provider for the agents.

        Parameters
        ----------
        None
        ----------
        Returns None
        """


        if self.new_agents:
            self.data_from = self.data_date_from()

            data_provider = DataProvider(self.data_from, self.end_date, self.tickers)
            market_provider = DataProvider(self.data_from, self.end_date, self.market_tickers)

            self.data = data_provider.provide()
            self.market = market_provider.provide()

            print("DAATTTAAA")
            print(self.data)
            print(self.data.isnull().values.any())

            if self.tickers != self.data.columns.to_list():
                self.tickers = self.data.columns.values
                print('Tickers succesfully set to data_columns, because tickers didnt match data.columns. Check data')

            if self.data_from is None:
                raise ValueError("You have to provide agents for evaluations")


    def add_agent(self, agent: Agent):
        """
        Adds an agent to the simulation/

        Parameters
        ----------
        agent : Agent
            Agent object to be used for simulation.
        ----------
        Returns None
        """
        self.agents.append(agent)
        self.new_agents.append(agent)

    def remove_agent(self, agent):
        """
        Removes an already added agent from the simulation.
        Paramters
        ----------
        agent : Agent
            Agent object to be removed from the simulation.
        ----------
        Returns None
        """
        try:
            self.agents.remove(agent)
        except ValueError:
            raise Warning("Model was not found in the evaluator")

    def clear_agents(self):
        """
        Deletes all agents from the simulation. Results will be still be available.

        Parameters
        ----------
        None
        ----------
        Returns None
        """
        self.agents = []


    def agents_allocate(self):
        """
        In this method all agents, one by one, predict their backtests for the simulation period.

        Parameters
        ----------
        None
        ----------
        Returns None
        """
        for agent in self.new_agents:
            print(f"Predictions for {agent}, are being calculated.")
            agent.weights_allocate(self.start_date, self.end_date, self.tickers, self.data)
            print(f"Predictions for {agent}, done.\n")

    def evaluate_agents(self, benchmarks=None):
        """
        This is where the agents are evaluated based on specified benchmarks. Returns a dictionary that has as keys,
        the frequencies of the benchmarks, e.g. "D" for daily benchmarks, "W" for weekly etc. and as values the
        DataFrames of the specified frequencies with all the benchmarks associated with them.

        Parameters
        ----------
        benchmarks: List[Benchmark]
            Benchmarks that the agents will be evaluated at.
        ----------
        return: Dictionary with the specified format.
        """
        try:

            weight_predictions = self.agents[0].weight_predictions
        except:
            raise ValueError(
                "Agents haven't decided their weights for the whole period yet, please run agent.weights_allocate first!"
            )

        results = {
            "D": pd.DataFrame(index=weight_predictions.groupby([weight_predictions.index.date]).sum().index),
            "W": pd.DataFrame(index=weight_predictions.groupby([weight_predictions.index.year, weight_predictions.index.isocalendar().week]).sum().index),
            "M": pd.DataFrame(index=weight_predictions.groupby([weight_predictions.index.month]).sum().index),
            "Y": pd.DataFrame(index=weight_predictions.groupby([weight_predictions.index.year]).sum().index),
            "YM": pd.DataFrame(index=weight_predictions.groupby([weight_predictions.index.year, weight_predictions.index.month]).sum().index),
            "P": pd.DataFrame(),
        }

        self.data = self.data[(self.data.index.date >= self.start_date) & (self.data.index.date <= self.end_date)]
        self.market = self.market[(self.market.index.date >= self.start_date) & (self.market.index.date <= self.end_date)]

        for agent in self.agents:
            self.results[agent.sheet_name()] = copy.deepcopy(results)
            for benchmark in benchmarks:
                benchmark_result = benchmark.calculate(agent.weight_predictions, self.tickers, self.data, self.market)
                self.results[agent.sheet_name()][benchmark.freq][benchmark.name] = benchmark_result
        return self.results

    def run(self):
        """
        Runs the simulation for all agents added. After the run has ended all agents have their predictions and
        quantities calculated.

        Parameters
        ----------
        None
        ----------
        Returns None
        """
        # Get data
        self.get_data()

        # Agents calculate the weight allocations
        self.agents_allocate()

    def run_n_evaluate(self):
        """
        Runs the simulation and evaluate the agents. Returns the dictionary with the results.

        Parameters
        ----------
        None
        ----------
        return: Dictionary with the specified format see evaluate_agents for details on format.
        """
        # Run first
        self.run()

        # Evaluate the agents based on the actual prices
        results = self.evaluate_agents(self.benchmarks)

        return results

    def results_to_excel2(self, filename: str, save_dir=".", disp=False):
        """
        Export the results of the simulation to an Excel file and display them in the console.

        Paramters
        ----------
        filename: str
            Filename of the Excel file.
        save_dir: str
            Directory in which the file will be saved relative to the backtesting project.
        disp: bool
            Boolean parameter to print results in the console.
        """
        if not self.results:
            raise ValueError("Please run evaluate_agents first to generate the results.")

        # Construct file path
        filepath = os.path.abspath(os.path.join(save_dir, filename))
        count = 1
        while os.path.exists(filepath):
            name, ext = os.path.splitext(filename)
            filepath = os.path.abspath(os.path.join(save_dir, f"{name} ({count}){ext}"))
            count += 1

        if self.excel_writer is None:
            self.excel_writer = pd.ExcelWriter(filepath)
        else:
            if filepath != self.excel_writer.path:
                self.excel_writer.save()
                self.excel_writer = pd.ExcelWriter(filepath)

        # Create a new Excel writer
        with pd.ExcelWriter(filepath) as writer:
            for agent, agent_results in self.results.items():
                if disp:
                    print(f"Agent: {agent}")

                row = 0
                for frequency, frequency_results in agent_results.items():
                    if frequency_results.empty:
                        continue

                    if disp:
                        print(f"\nFrequency: {frequency}")
                        print(frequency_results)

                    try:
                        # write results to Excel
                        frequency_results.to_excel(writer, sheet_name=agent[:31],  # Excel sheet name limit is 31 characters
                            startrow=row, float_format="%.6f", )
                        row += frequency_results.shape[0] + 2  # Leave a gap between sections
                    except Exception as ex:
                        raise ValueError(f"Failed to write to Excel: {ex}")

                print('\n')

        if disp:
            print(f"\nResults successfully saved to: {filepath}")
