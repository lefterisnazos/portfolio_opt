import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_hrp_weights(hrp_weights, period):
    """
    Plots the HRP weights for the given period.

    Parameters:
        hrp_weights (dict): HRP weights for the stocks.
        weights_df (DataFrame): Weights DataFrame to determine the period.
    """
    stock_numbers = range(1, len(hrp_weights) + 1)
    if isinstance(hrp_weights, pd.Series):
        weights = hrp_weights.to_list()
    else:
        weights = list(hrp_weights.values())

    plt.figure(figsize=(10, 6))
    plt.plot(stock_numbers, weights, marker='o', linestyle='-', color='b')

    plt.xlabel('Stock Number', fontsize=12)
    plt.ylabel('Weight', fontsize=12)
    plt.title(f'HRP Weights for the {period}-month period', fontsize=14)

    plt.xticks(stock_numbers)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.show()