"""
This module includes functions for analyzing and visualizing missing values.
"""

import matplotlib.pyplot as plt

import seaborn as sns


def plot_heatmap_missing_values_daily(df):
    """
    Generate a heatmap to visualize daily missing values in a DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to be analyzed for missing values.

    Returns:
        plt: A Matplotlib figure representing the heatmap of missing values.
    """
    # Group by day and check for any missing values for each day
    missing_data = df.resample("D").apply(lambda x: x.isnull().any())

    # Determine the number of days (rows) in your dataframe
    num_days = missing_data.shape[0]

    # Set the height of the figure based on the number of days, and a fixed width
    plt.figure(figsize=(10, num_days * 0.15 + 3))

    sns.heatmap(missing_data, cmap="Greens_r", cbar=False)

    # Set y-tick labels to represent each day
    plt.yticks(range(num_days), missing_data.index.date, rotation=0)

    plt.title("Heatmap of Missing Values (white = missing)")
    plt.tight_layout()

    return plt


def print_df_info(df):
    """
    prints df info for intermediate checks or debugging
    """
    info = df.info()
    print(info)
