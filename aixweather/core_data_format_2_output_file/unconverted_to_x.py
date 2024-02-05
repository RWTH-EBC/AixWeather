"""
converts core data to different simpler formats (currently without any transformation)
"""

import logging
import json
import pickle
import pandas as pd

from aixweather import definitions
from aixweather.imports.utils_import import MetaData


logger = logging.getLogger(__name__)


def _get_file_name_and_meta_data_file_name(
        meta: MetaData, suffix: str, filename: str = None
) -> (str, str):
    """
    Return the filename and meta-data filename for the given suffix
    """
    if filename is None:
        filename = f"Station_{meta.station_name}.{suffix}"
        meta_filename = f"Station_{meta.station_name}_meta_data.{suffix}"
    else:
        meta_filename = filename.replace(f".{suffix}", f"_meta_data.{suffix}")
    return filename, meta_filename


def to_pickle(
    core_df: pd.DataFrame,
    meta: MetaData,
    result_folder: str = None,
    filename: str = None
) -> (pd.DataFrame, str):
    """Create and save a pickle file from the core data.

    Args:
        core_df (pd.DataFrame): DataFrame containing core data.
        meta (MetaData): Metadata associated with the data.
        result_folder (str):
            Path to the folder where to save the file. Default will use
            the `results_file_path` method.
        filename (str): Name of the file to be saved. The default is constructed
            based on the station name.

    Returns:
        pd.DataFrame: DataFrame containing the weather data formatted as core data.
        str: Path to the exported file.
    """

    core_df = core_df.copy()
    filename, meta_filename = _get_file_name_and_meta_data_file_name(
        meta=meta, filename=filename, suffix="pkl"
    )
    file_path = definitions.results_file_path(filename, result_folder)
    meta_file_path = definitions.results_file_path(meta_filename, result_folder)

    core_df.to_pickle(file_path)
    with open(meta_file_path, "wb") as file:
        pickle.dump(meta, file)

    logger.info("Pickle saved to %s, meta information saved to %s.", file_path, meta_file_path)

    return core_df, file_path


def to_json(
    core_df: pd.DataFrame,
    meta: MetaData,
    result_folder: str = None,
    filename: str = None
) -> (pd.DataFrame, str):
    """Create and save a json file from the core data.

    Args:
        core_df (pd.DataFrame): DataFrame containing core data.
        meta (MetaData): Metadata associated with the data.
        result_folder (str):
            Path to the folder where to save the file. Default will use
            the `results_file_path` method.
        filename (str): Name of the file to be saved. The default is constructed
            based on the station name.

    Returns:
        pd.DataFrame: DataFrame containing the weather data formatted as core data.
        str: Path to the exported file.
    """

    core_df = core_df.copy()

    filename, meta_filename = _get_file_name_and_meta_data_file_name(
        meta=meta, filename=filename, suffix="json"
    )
    file_path = definitions.results_file_path(filename, result_folder)
    meta_file_path = definitions.results_file_path(meta_filename, result_folder)

    # Convert DataFrame to JSON and save to file
    core_df.to_json(file_path, orient="records")

    # Convert meta_data to a dictionary and save to JSON file
    meta_dict = meta.__dict__  # Convert the meta_data object to a dictionary
    with open(meta_file_path, "w") as file:
        json.dump(meta_dict, file, indent=4)

    logger.info("JSON saved to %s, meta information saved to %s.", file_path, meta_file_path)

    return core_df, file_path


def to_csv(
    core_df: pd.DataFrame,
    meta: MetaData,
    result_folder: str = None,
    filename: str = None
) -> (pd.DataFrame, str):
    """Create and save a csv file from the core data.

    Args:
        core_df (pd.DataFrame): DataFrame containing core data.
        meta (MetaData): Metadata associated with the data.
        result_folder (str):
            Path to the folder where to save the file. Default will use
            the `results_file_path` method.
        filename (str): Name of the file to be saved. The default is constructed
            based on the station name.

    Returns:
        pd.DataFrame: DataFrame containing the weather data formatted as core data.
        str: Path to the exported file.
    """

    core_df = core_df.copy()

    filename, meta_filename = _get_file_name_and_meta_data_file_name(
        meta=meta, filename=filename, suffix="csv"
    )
    file_path = definitions.results_file_path(filename, result_folder)
    meta_file_path = definitions.results_file_path(meta_filename, result_folder)

    core_df.to_csv(file_path, index=True)

    # Convert meta_data to a dictionary and save to JSON file
    meta_dict = meta.__dict__  # Convert the meta_data object to a dictionary
    with open(meta_file_path, "w") as file:
        json.dump(meta_dict, file, indent=4)

    logger.info("CSV saved to %s, meta information saved to %s.", file_path, meta_file_path)

    return core_df, file_path
