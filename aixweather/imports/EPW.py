"""
import epw files
"""

import pandas as pd

from aixweather.imports.utils_import import MetaData


def load_epw_meta_from_file(path: str) -> MetaData:
    """
    Load an EPW file from a specified path and parse the file header for metadata.

    Args:
        path (str): The file path to the EPW file to be loaded.

    Returns:
        MetaData: An object containing the parsed metadata from the EPW file.
    """

    meta = MetaData()

    with open(path, "r", encoding="latin1") as file:
        lines = file.readlines()

    # The 1st line contains the location data
    location_data = lines[0].split(",")

    meta.station_name = location_data[1]
    meta.latitude = float(location_data[6])
    meta.longitude = float(location_data[7])
    meta.timezone = float(location_data[8])
    meta.altitude = float(location_data[9])
    meta.input_source = "EPW"

    return meta


def load_epw_from_file(path: str) -> pd.DataFrame:
    """
    Import data from an EPW file and convert it into a DataFrame.

    Args:
        path (str): The absolute path to the EPW file.

    Returns:
        pd.DataFrame: A DataFrame containing the imported data from the EPW file.
    """


    # Find the row number for "DATA PERIODS" to determine where the data starts
    with open(path, "r", encoding="latin1") as file:
        lines = file.readlines()
        data_start_row = (
                next(i for i, line in enumerate(lines) if "DATA PERIODS" in line) + 1
        )

    # Skipping header rows to load data
    weather_df = pd.read_csv(
        path,
        skiprows=data_start_row,
        header=None,
        encoding="latin1",
        encoding_errors="replace",
    )

    return weather_df
