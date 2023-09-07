"""
converts core data to different simpler formats (currently without any transformation)
"""

import json
import pickle
import pandas as pd

from aixweather import definitions
from aixweather.imports.utils_import import MetaData


def to_pickle(
    core_df: pd.DataFrame,
    meta: MetaData,
    result_folder: str = None
):
    """Create and save a pickle file from the core data.

    Args:
        core_df (pd.DataFrame): DataFrame containing core data.
        meta (MetaData): Metadata associated with the data.

    Returns:
        pd.DataFrame: DataFrame containing the weather data formatted as core data.
    """

    core_df = core_df.copy()
    filename = f"Station_{meta.station_name}.pkl"
    meta_filename = f"Station_{meta.station_name}_meta_data.pkl"
    file_path = definitions.results_file_path(filename, result_folder)
    meta_file_path = definitions.results_file_path(meta_filename, result_folder)

    core_df.to_pickle(file_path)
    with open(meta_file_path, "wb") as file:
        pickle.dump(meta, file)

    print(f"Pickle saved to {file_path}, meta information saved to {meta_file_path}.")

    return core_df


def to_json(
    core_df: pd.DataFrame,
    meta: MetaData,
    result_folder: str = None
):
    """Create and save a json file from the core data.

    Args:
        core_df (pd.DataFrame): DataFrame containing core data.
        meta (MetaData): Metadata associated with the data.

    Returns:
        pd.DataFrame: DataFrame containing the weather data formatted as core data.
    """

    core_df = core_df.copy()

    filename = f"Station_{meta.station_name}.json"
    meta_filename = f"Station_{meta.station_name}_meta_data.json"
    file_path = definitions.results_file_path(filename, result_folder)
    meta_file_path = definitions.results_file_path(meta_filename, result_folder)

    # Convert DataFrame to JSON and save to file
    core_df.to_json(file_path, orient="records")

    # Convert meta_data to a dictionary and save to JSON file
    meta_dict = meta.__dict__  # Convert the meta_data object to a dictionary
    with open(meta_file_path, "w") as file:
        json.dump(meta_dict, file, indent=4)

    print(f"JSON saved to {file_path}, meta information saved to {meta_file_path}.")

    return core_df


def to_csv(
    core_df: pd.DataFrame,
    meta: MetaData,
    result_folder: str = None
):
    """Create and save a csv file from the core data.

    Args:
        core_df (pd.DataFrame): DataFrame containing core data.
        meta (MetaData): Metadata associated with the data.

    Returns:
        pd.DataFrame: DataFrame containing the weather data formatted as core data.
    """

    core_df = core_df.copy()

    filename = f"Station_{meta.station_name}.csv"
    meta_filename = f"Station_{meta.station_name}_meta_data.json"
    file_path = definitions.results_file_path(filename, result_folder)
    meta_file_path = definitions.results_file_path(meta_filename, result_folder)

    core_df.to_csv(file_path, index=True)

    # Convert meta_data to a dictionary and save to JSON file
    meta_dict = meta.__dict__  # Convert the meta_data object to a dictionary
    with open(meta_file_path, "w") as file:
        json.dump(meta_dict, file, indent=4)

    print(f"CSV saved to {file_path}, meta information saved to {meta_file_path}.")

    return core_df
