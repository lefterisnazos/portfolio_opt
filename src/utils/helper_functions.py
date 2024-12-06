import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_weights(hrp_weights, period):
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
    plt.title(f'Final model Weights for the {period}-month period', fontsize=14)

    plt.xticks(stock_numbers)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.show()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.dates as mdates


def plot_weights_3d(weight_predictions):
    """
    Plots a 3D visualization of weights over time for given tickers.

    Parameters:
    -----------
    weight_predictions: pd.DataFrame
        DataFrame where rows represent dates (index), columns represent tickers,
        and values represent allocated weights.
    """
    # Ensure data is numeric and handle missing values
    weight_predictions = weight_predictions.fillna(0).astype(float)

    # Convert dates to numeric and create meshgrid
    dates = mdates.date2num(weight_predictions.index.to_pydatetime())
    assets = np.arange(len(weight_predictions.columns))  # Numeric indices for assets

    X, Y = np.meshgrid(dates, assets)

    # Align Z values
    Z = weight_predictions.T.values  # Transpose to align assets (rows) and dates (columns)
    print(f"X shape: {X.shape}, Y shape: {Y.shape}, Z shape: {Z.shape}")

    # Replace NaNs if present
    Z = np.nan_to_num(Z)

    # Create the 3D plot
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Plot the surface
    surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='k')

    # Formatting
    ax.set_title('3D Plot of Allocated Weights Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Assets')
    ax.set_zlabel('Weights')

    # Format the x-axis to show dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)

    # Add color bar for weights
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)

    plt.show()


# Example Usage:  # Assuming `weights_allocate` has been called and the result is stored in `weight_predictions`  # plot_weights_3d(weight_predictions)
