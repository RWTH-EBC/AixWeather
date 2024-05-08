"""
This module includes functions for analyzing and visualizing missing values.
"""

import matplotlib.pyplot as plt

import seaborn as sns


def plot_heatmap_missing_values(df):
    """
    Generate a heatmap to visualize missing values in a DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to be analyzed for missing values.

    Returns:
        plt: A Matplotlib figure representing the heatmap of missing values.
    """

    # define resolution depending on the length of the data set
    if len(df) <= (24 * 60):
        resolution = "D"
        res_name = "daily"
    elif len(df) <= (24 * 7 * 60):
        resolution = "W"
        res_name = "weekly"
    else:
        resolution = "M"
        res_name = "monthly"

    # Group by resolution and check for missing values in each period
    missing_data = df.resample(resolution).apply(lambda x: x.isnull().mean())

    # Determine the number rows to plot
    num_rows = missing_data.shape[0]

    # Set the height of the figure based on the number of rows, and a fixed width
    plt.figure(figsize=(14, num_rows * 0.15 + 3))

    sns.heatmap(
        missing_data,
        cmap="Greens_r",
        cbar=True,
        yticklabels=False  # Remove y-axis labels
    )

    # Set y-tick labels to represent each period
    plt.yticks(range(num_rows), missing_data.index.date, rotation=0)

    plt.title("Heatmap of data availability\n"
              "From white (100% data missing) to dark green (0% data missing)\n"
              f"Bucket size = {res_name}")
    plt.tight_layout()

    return plt


def print_df_info(df):
    """
    prints df info for intermediate checks or debugging
    """
    info = df.info()
    print(info)
