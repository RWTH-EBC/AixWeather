"""
import DWD TRY data
"""

import datetime as dt
import re
import pandas as pd

import geopandas as gpd
from geopy.geocoders import Nominatim
from shapely.geometry import Point

from AixWeather.imports.utils_import import MetaData


def _handle_TRY_type(path: str) -> tuple:
    """
    Determine the TRY format type based on the provided file path.

    Args:
        path (str): The file path to the TRY dataset file.

    Returns:
        tuple: A tuple containing the TRY year (int) and the header row number (int).
    Raises:
        ValueError: If the TRY format cannot be detected through the file name or is not supported.
    """

    ### get type of TRY, i.e. the year of the TRY
    TRY_year = None
    # Header_rows are the rows with general information of the dataset
    # Are skipped until variable declaration
    TRY_file_naming = {
        "TRY2004": {"year": 2004},
        "TRY2010": {"year": 2010},
        "TRY2015": {"year": 2015},
        "TRY2045": {"year": 2045},
    }

    if path.endswith(".dat"):
        for key in TRY_file_naming.keys():
            if key in path:
                TRY_year = TRY_file_naming[key]["year"]
                break
    if TRY_year is None:
        raise ValueError(
            f"TRY format could not be detected through file name,"
            f" expected {[key for key in TRY_file_naming.keys()]} in the file name."
        )
    if TRY_year == 2004 or TRY_year == 2010:
        raise ValueError(f"TRY format {TRY_year} is not supported.")

    if TRY_year == 2015 or TRY_year == 2045:
        with open(path, "r") as file:
            for line_number, line in enumerate(file, start=1):
                if "***" in line:
                    header_row = (
                        line_number - 1 - 1
                    )  # -1 for header above *** and -1 for start to count at 0
                    break

    return TRY_year, header_row


def load_try_meta_from_file(path: str) -> MetaData:
    """
    Load a TRY file from a specified path and parse the header for metadata.

    Args:
        path (str): The file path to the TRY file to be loaded.

    Returns:
        MetaData: An object containing the parsed metadata from the TRY file.
    """

    meta = MetaData()
    TRY_year, header_row = _handle_TRY_type(path)

    ### load file to python
    header_lines = []
    with open(path, "r") as file:
        for i, line in enumerate(file):
            if i >= header_row:
                break
            header_lines.append(line)

    ### read raw meta data
    # Extract Rechtswert (Easting)
    rechtswert_line = next(
        line for line in header_lines if "Rechtswert" in line and ":" in line
    )
    rechtswert = int(re.search(r":\s*(\d+) Meter", rechtswert_line).group(1))

    # Extract Hochwert (Northing)
    hochwert_line = next(
        line for line in header_lines if "Hochwert" in line and ":" in line
    )
    hochwert = int(re.search(r":\s*(\d+) Meter", hochwert_line).group(1))

    # Extract Höhenlage (altitude)
    hoehenlage_line = next(line for line in header_lines if "Hoehenlage" in line)
    hoehenlage = int(re.search(r":\s*(\d+) Meter", hoehenlage_line).group(1))

    ### convert latitude and longitude
    # Create a GeoDataFrame with the provided coordinates
    # (using pyproj directly led to wrong calculation)
    gdf = gpd.GeoDataFrame(
        {"geometry": [Point(rechtswert, hochwert)]},
        crs="EPSG:3034",  # Original coordinate system
    )

    # Transform to WGS 84
    gdf_wgs84 = gdf.to_crs("EPSG:4326")

    # get transformed coordinates, Get the longitude (x) and latitude (y)
    point_wgs84 = gdf_wgs84.geometry.iloc[0]
    longitude_wgs84 = point_wgs84.x
    latitude_wgs84 = point_wgs84.y

    ### try to get city of location
    # Initialize Nominatim geolocator
    geolocator = Nominatim(user_agent="myGeocoder")
    try:
        # Perform reverse geocoding
        location = geolocator.reverse((latitude_wgs84, longitude_wgs84))

        # If you want specific components like city, state, etc.
        address = location.raw["address"]
        if "city" in address:
            city = address["city"]
        elif "town" in address:
            city = address["town"]
        elif "village" in address:
            city = address["village"]
        elif "hamlet" in address:
            city = address["hamlet"]
        elif "suburb" in address:
            city = address["suburb"]
        elif "locality" in address:
            city = address["locality"]
        else:
            city = "Unknown"
    except:
        city = meta.station_name
        print(
            "Error: could not infer closest city from longitude + latitude"
            " -> station_name will be unknown."
        )

    meta.station_name = city
    meta.input_source = f"TRY{TRY_year}"
    meta.altitude = hoehenlage
    meta.longitude = longitude_wgs84
    meta.latitude = latitude_wgs84

    return meta


def load_try_from_file(path: str) -> pd.DataFrame:
    """
    Import data from a TRY file and convert it into a DataFrame.

    Args:
        path (str): The absolute path to the TRY file.

    Returns:
        pd.DataFrame: A DataFrame containing the imported data from the TRY file.
    """


    TRY_year, header_row = _handle_TRY_type(path)

    ### load file to Dataframe
    weather_df = pd.read_table(
        filepath_or_buffer=path,
        header=header_row,
        delim_whitespace=True,
        skip_blank_lines=False,
        encoding="latin",
    )
    # drop first row cause empty
    weather_df = weather_df.iloc[1:]

    # set index to datetime
    # returns datetime objects
    weather_df["MM"] = weather_df["MM"].astype(int)
    weather_df["DD"] = weather_df["DD"].astype(int)
    weather_df["HH"] = weather_df["HH"].astype(int)
    time_index = weather_df.apply(
        lambda row: dt.datetime(int(TRY_year), row.MM, row.DD, row.HH - int(1.0)),
        axis=1,
    )
    # data is shifted by -1 H to satisfy pandas timestamp
    # hours in pandas only between 0 and 23, in TRY between 1 and 24
    # converts to pandas timestamps if desired
    weather_df.index = pd.to_datetime(time_index)
    # data is shifted back to original to start: back to
    # 2017-01-01 01:00:00 instead of the temporary 2017-01-01 00:00:00
    weather_df = weather_df.shift(periods=1, freq="H", axis=0)

    return weather_df
