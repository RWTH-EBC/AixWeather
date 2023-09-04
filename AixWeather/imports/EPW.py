"""
import epw files
"""

import pandas as pd

from AixWeather.imports.utils_import import MetaData


def load_epw_meta_from_file(path: str):
    """
    Loads an EPW file from a path and parses the header for
    meta information and saves it in the meta_class.
    """

    meta = MetaData()

    with open(path, "r") as file:
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


def load_epw_from_file(path):
    """
    Import data from EPW file and convert them into df

        Parameters:
            path: (string) absolute path to file

        Return:
            df
    """

    # Find the row number for "DATA PERIODS" to determine where the data starts
    with open(path, "r") as file:
        lines = file.readlines()
        data_start_row = (
                next(i for i, line in enumerate(lines) if "DATA PERIODS" in line) + 1
        )

    # Skipping header rows to load data
    weather_df = pd.read_csv(
        path,
        skiprows=data_start_row,
        header=None,
        encoding="ISO-8859-1",
        encoding_errors="replace",
    )

    # The first 4 columns represent year, month, day, and hour respectively,
    # but with hour 24 instead of hour 0.
    hour = weather_df.iloc[:, 3].copy()
    mask_24hr = hour == 24
    hour.loc[mask_24hr] = 0
    weather_df["datetime"] = pd.to_datetime(
        weather_df.iloc[:, 0].astype(str)
        + "-"
        + weather_df.iloc[:, 1].astype(str)
        + "-"
        + weather_df.iloc[:, 2].astype(str)
        + " "
        + hour.astype(str)
        + ":00:00"
    )

    # Increment the day by one for those rows where hour
    # was originally 24
    weather_df.loc[mask_24hr, "datetime"] = weather_df.loc[mask_24hr, "datetime"] \
                                            + pd.Timedelta(days=1)

    # Setting datetime column as index
    weather_df.set_index("datetime", inplace=True)

    return weather_df
