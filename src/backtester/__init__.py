import pandas as pd
from src.agents import Agent
import copy
from src. DataProvider import DataProvider
import os
from src.models.base import WeightAllocationModel

class Backtester:

    def __init__(self,start_date, end_date, ticker_list, benchmarks, save=False):
        self.start_date = start_date
        self.end_date = end_date
        self.tickers = ticker_list
        self.benchmarks = benchmarks

        self.data_from = None
        self.data = None

        self.agents = []
        self.new_agents = []
        self.changed_agents = []
        self.benchmarks = benchmarks
        self.results = {}
        self.excel_writer = None

        self.save = save
        WeightAllocationModel.save = save

    def data_date_from(self):

        date_from = self.start_date
        for agent in self.agents:
            temp = agent.date_data_needed(self.start_date, self.end_date)
            if pd.Timestamp(temp) < pd.Timestamp(date_from):
                date_from = temp

        return date_from

    def get_data(self):

        if self.new_agents:
            self.data_from = self.data_date_from()
            data_provider = DataProvider(self.data_from, self.end_date, self.tickers)
            self.data = data_provider.fetch()

            if self.data_from is None:
                raise ValueError("You have to provide agents for evaluations")

    def add_agent(self, agent: Agent):
        """
        Adds an agent to the simulation/
        :param agent: Agent object to be used for simulation
        """
        self.agents.append(agent)
        self.new_agents.append(agent)

    def remove_agent(self, agent):
        """
        Removes an already added agent from the simulation.
        :param agent: Agent instance of the agent you want to be removed.
        """
        try:
            self.agents.remove(agent)
        except ValueError:
            raise Warning("Model was not found in the evaluator")

    def clear_agents(self):
        """
        Deletes all agents from the simulation. Results will be still be available.
        """
        self.agents = []


    def agents_allocate(self):
        """
        In this method all agents, one by one, predict their backtests for the simulation period.
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
        :param benchmarks: Benchmarks that the agents will be evaluated at.
        :return: Dictionary with the specified format.
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
        # VERY IMPORTANT FOR INDEX MATCHING OR EVERYTHING AFTER THIS POINT ON PIPELINE IS FUCKED --> index of agent.weight_predictions and self.data should have same index at this point.
        for agent in self.agents:
            self.results[agent.sheet_name()] = copy.deepcopy(results)
            for benchmark in benchmarks:
                benchmark_result = benchmark.calculate(agent.weight_predictions, self.tickers, self.data)
                self.results[agent.sheet_name()][benchmark.freq][benchmark.name] = benchmark_result
        return self.results

    def run(self):
        """
        Runs the simulation for all agents added. After the run has ended all agents have their predictions and
        quantities calculated.
        """
        # Get data
        self.get_data()

        # Agents calculate the weight allocations
        self.agents_allocate()

    def run_n_evaluate(self):
        """
        Runs the simulation and evaluate the agents. Returns the dictionary with the results.
        :return: Dictionary with the specified format see evaluate_agents for details on format.
        """
        # Run first
        self.run()

        # Evaluate the agents based on the actual prices
        results = self.evaluate_agents(self.benchmarks)

        return results

    def results_to_excel2(self, filename: str, save_dir=".", disp=False):
        """
        Export the results of the simulation to an Excel file and display them in the console.
        :param filename: Filename of the Excel file.
        :param save_dir: Directory in which the file will be saved relative to the backtesting project.
        :param disp: Boolean parameter to print results in the console.
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

        if disp:
            print(f"\nResults successfully saved to: {filepath}")
