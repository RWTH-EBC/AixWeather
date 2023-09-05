"""
contains functions to handle data within ERC
"""

from tkinter import *
import json
import pandas as pd
from datetime import datetime

import requests

from AixWeather.imports.utils_import import MetaData

key_list = [
    "4121.weatherstation.temperature",
    "4121.weatherstation.diffuse-radiation",
    "4121.weatherstation.global-radiation",
    "4121.weatherstation.pressure",
    "4121.weatherstation.rainfall",
    "4121.weatherstation.relative-humidity",
    "4121.weatherstation.wind-direction",
    "4121.weatherstation.wind-speed",
]


def load_credentials_ERC_weather_data() -> tuple:
    """
    GUI to return the username and password needed to access ERC weather data.

    Returns:
        tuple: The username and password required for accessing ERC weather data.
    """


    tk_window = Tk()
    tk_window.geometry("400x150")
    tk_window.title(
        "ERC is a private database, credentials are required to acquire the data"
    )

    # username label and text entry box
    username_label = Label(tk_window, text="User Name").grid(row=0, column=0)
    username = StringVar()
    username_entry = Entry(tk_window, textvariable=username).grid(row=0, column=1)

    # password label and password entry box
    password_label = Label(tk_window, text="Password").grid(row=1, column=0)
    password = StringVar()
    password_entry = Entry(tk_window, textvariable=password, show="*").grid(
        row=1, column=1
    )
    # login button
    login_button = Button(tk_window, text="Login", command=tk_window.destroy).grid(
        row=4, column=0
    )

    tk_window.mainloop()

    return (username.get(), password.get())


def import_ERC(start: datetime, stop: datetime, cred: tuple) -> pd.DataFrame:
    """
    Import weather data from aedifion ERC weather station (credentials required).

    Args:
        start (datetime): Datetime object representing the data start.
        stop (datetime): Datetime object representing the data stop.
        cred (tuple): Aedifion credentials.

    Returns:
        pd.DataFrame: DataFrame containing as raw as possible weather data from aedifion ERC.
    """

    # import cred if not given
    if cred is None:
        cred = load_credentials_ERC_weather_data()

    weather_df_tot = pd.DataFrame()

    for key in key_list:
        request = {
            "project_id": 11,
            "dataPointID": key,
            "start": start,
            "end": stop,
            "interpolation": "null",
            "samplerate": "1h",
            "short": "True",
        }
        response = requests.get(
            "https://api.ercebc.aedifion.io/v2/" + "datapoint/timeseries",
            auth=cred,
            params=request,
        )
        # Check for errors
        response.raise_for_status()

        # continue loading
        api_response = response.json()
        weather_df = _json2df(api_response, data_point_id=key)

        if not weather_df.empty:
            if weather_df_tot.empty:
                # If the main DataFrame is empty, simply assign the first DataFrame to it
                weather_df_tot = weather_df
            else:
                weather_df_tot = pd.merge(
                    weather_df_tot, weather_df, how="outer", left_index=True, right_index=True
                )

    return weather_df_tot


def import_meta_from_ERC() -> MetaData:
    """
    Import (specify) metadata from ERC.

    Returns:
        MetaData: A MetaData object containing station information for ERC.
    """

    meta = MetaData()
    meta.station_id = "ERC"
    meta.station_name = "Old_Experimental_Hall"
    meta.altitude = 230  # ca. 200m + building height 30m
    meta.latitude = 50.7893
    meta.longitude = 6.0516
    return meta


def _json2df(
    data: json = None, data_point_id: str = None, short: bool = True
) -> pd.DataFrame:
    """
    Transform the JSON returned by GET /v2/datapoint/timeseries to a Pandas DataFrame
    indexed by time.

    Args:
        data (json): The JSON data to be transformed into a DataFrame.
        data_point_id (str): Use dataPointID as the column name for values (default: value).
        short (bool): Whether the given JSON is in short format or not.

    Returns:
        pd.DataFrame: A Pandas DataFrame containing the transformed data.
    """
    if short:
        data = [[pd.to_datetime(t[0], utc=True), t[1]] for t in data]
    else:
        data = [[pd.to_datetime(t["time"], utc=True), t["value"]] for t in data["data"]]
    dataframe = pd.DataFrame(data, columns=["Time", data_point_id or "Value"])
    dataframe = dataframe.set_index("Time")
    return dataframe
