"""
imports weather data from the DWD
"""

import zipfile
import os
import shutil
import datetime as dt
import urllib.request
import pandas as pd

from wetterdienst.provider.dwd.mosmix import DwdMosmixRequest, DwdMosmixType

from aixweather.imports import utils_import
from aixweather import definitions


def import_DWD_historical(start: dt.datetime, station: str) -> pd.DataFrame:
    """
    Pull historical data from DWD:
    (https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/) and
    format them into a dataframe.

    Args:
        start: defines how much data must be pulled
        station: station id of the DWD

    Returns:
        Dataframe weather data from DWD that is as raw as possible.
    """
    measurements = [
        "air_temperature",
        "solar",
        "wind",
        "precipitation",
        "soil_temperature",
        "cloudiness",
    ]

    base_url = (
        "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/"
    )

    # if start of datapoint older than 530 days from now -> import data from historical folder too
    days_from_now = (dt.datetime.now() - start).days
    if days_from_now >= (530 - 1):
        historical_folder = True
    else:
        historical_folder = False

    # create dataframe in which all data to be stored
    df_w_ges = pd.DataFrame()

    # get weather data from dwd per measurement
    for single_measurement in measurements:
        # inconsistent pathing from DWD resolved by using the 10-min Values for these measurements
        if single_measurement == "solar" or single_measurement == "air_temperature":
            df_w = _pull_DWD_historical_data(
                f"{base_url}/10_minutes/{single_measurement}/recent/",
                station=station,
            )
            if historical_folder:
                df_hist = _pull_DWD_historical_data(
                    f"{base_url}/10_minutes/{single_measurement}/historical/",
                    station=station,
                )
                # add up rows (time periods)
                df_w = pd.concat([df_w, df_hist])
                # dataframes may overlap with same values, delete duplicates
                df_w = df_w[~df_w.index.duplicated(keep="first")]
        else:
            df_w = _pull_DWD_historical_data(
                f"{base_url}/hourly/{single_measurement}/recent/",
                station=station,
            )
            if historical_folder:
                df_hist = _pull_DWD_historical_data(
                    f"{base_url}/hourly/{single_measurement}/historical/",
                    station=station,
                )
                # add up rows (time periods)
                df_w = pd.concat([df_w, df_hist])
                # dataframes may overlap with same values, delete duplicates
                df_w = df_w[~df_w.index.duplicated(keep="first")]

        # concat each measurement (column)
        df_w_ges = pd.concat([df_w_ges, df_w], axis=1, join="outer", sort=True)

    return df_w_ges


def import_DWD_forecast(station: str) -> pd.DataFrame:
    """
    Import weather forecast data from the DWD (German Weather Service) for a specified station.

    Args:
        station (str): Station ID of the DWD for which forecast data is to be imported.
                       For debugging purposes: station 01028.

    Returns:
        pd.DataFrame: DataFrame containing weather forecast data from the DWD.
    """

    ### pull forecast data using the package wetterdienst
    stations = DwdMosmixRequest(
        parameter="small", mosmix_type=DwdMosmixType.SMALL
    ).filter_by_station_id(station_id=[station])
    # query object to get dataframe with forecast values
    try:
        values = next(stations.values.query())
    except Exception as excep:
        raise ValueError(f"There is no loadable forecast for station {station}") from excep

    imported_df = values.df.to_pandas()

    ### transform to one column per measurement
    # Convert the 'Timestamp' column to a datetime object
    imported_df["date"] = pd.to_datetime(imported_df["date"])

    # Set the 'Timestamp' column as the index
    imported_df.set_index("date", inplace=True)

    # Drop unnecessary columns
    imported_df.drop(columns=["station_id", "dataset", "quality"], inplace=True)

    # Pivot the dataframe to have each measurement as a separate column
    imported_df = imported_df.pivot(columns="parameter", values="value")

    return imported_df


def import_meta_DWD_historical(station:str) -> utils_import.MetaData:
    """
    Downloads and extracts metadata related to the specified station from
    the DWD (Deutscher Wetterdienst) Open Data Interface.

    Parameters:
        station: Station ID for which metadata is to be retrieved.

    Returns:
        meta (meta_data object): An object of the meta_data class with
        populated attributes related to the station.
    """

    url = "https://www.dwd.de/DE/leistungen/klimadatendeutschland/" \
          "statliste/statlex_rich.txt;jsessionid" \
          "=68E14BA255FE50BDC4AD9FF4F835895F.live31092?view=nasPublication&nn=16102"

    # load station overview
    data_str = urllib.request.urlopen(url).read().decode("latin-1")

    ### find station ID and its values
    # Splitting the data into lines
    lines = data_str.strip().split("\n")

    # Getting the header line and the line with dashes
    header_line = lines[0]
    dash_line = lines[1]

    # Finding the column breaks based on the dash line
    column_breaks = [0]
    for i in range(len(dash_line)):
        if dash_line[i] != "-" and (i == 0 or dash_line[i - 1] == "-"):
            column_breaks.append(i)
    column_breaks.append(len(dash_line))

    # Splitting the header line based on column breaks
    header = [
        header_line[start:end].strip()
        for start, end in zip(column_breaks[:-1], column_breaks[1:])
    ]

    # Initializing a dictionary to store the result
    station_data = {}

    # Iterating through the rows and finding the one with the desired STAT_ID
    for line in lines[2:]:
        values = [
            line[start:end].strip()
            for start, end in zip(column_breaks[:-1], column_breaks[1:])
        ]
        stat_id = str(values[header.index("STAT_ID")])
        if stat_id == station:
            station_data = {key: value for key, value in zip(header, values)}
            break
        else:
            raise ValueError(f"Station for historical weatherdata with ID {station} could not be"
                             f"found in station list {url}.")

    ### convert to meta class
    meta = utils_import.MetaData()
    meta.station_id = station_data["STAT_ID"]
    meta.station_name = station_data["STAT_NAME"]
    meta.altitude = station_data["HS"]
    meta.longitude = station_data["LA_HIGH"]
    meta.latitude = station_data["BR_HIGH"]
    meta.station_exists_since = station_data["BEGINN"]
    meta.station_exists_until = station_data["ENDE"]
    meta.input_source = "DWD Historical"

    return meta


def import_meta_DWD_forecast(station: str) -> utils_import.MetaData:
    """
    Downloads and extracts metadata related to the specified station
    from the DWD (Deutscher Wetterdienst) Open Data Interface.

    Parameters:
        station: Station ID for which metadata is to be retrieved.

    Returns:
        meta (meta_data object): An object of the meta_data class with
        populated attributes related to the station.
    """
    url = "https://www.dwd.de/DE/leistungen/met_verfahren_mosmix/" \
          "mosmix_stationskatalog.cfg?view=nasPublication&nn" \
          "=16102"

    # load station overview
    data_str = urllib.request.urlopen(url).read().decode("latin-1")

    ### find station ID and its values
    def extract_info_for_station(data_str, station_id):
        # Splitting the data by lines
        lines = data_str.strip().split("\n")

        # Iterating through the lines to find the desired ID
        for line in lines[2:]:
            # Splitting the line into parts
            parts = line.split()

            # Extracting the ID and checking if it matches the search ID
            id = parts[0]
            if id == station_id:
                # Creating a dictionary to store the details
                result_dict = {}
                result_dict["ID"] = id
                result_dict["ICAO"] = parts[1]
                result_dict["NAME"] = " ".join(parts[2:-3])
                result_dict["LAT"] = parts[-3]
                result_dict["LON"] = parts[-2]
                result_dict["ELEV"] = parts[-1]
                return result_dict

        # warn that the station does not exist
        raise ValueError(
            f"Station for forecast data with the ID {station_id} could not be found in the "
            f"station list: {url}"
        )

    station_data = extract_info_for_station(data_str, station)

    # convert to meta class
    meta = utils_import.MetaData()
    meta.station_id = station_data["ID"]
    meta.station_name = station_data["NAME"]
    meta.altitude = station_data["ELEV"]
    meta.longitude = station_data["LON"]
    meta.latitude = station_data["LAT"]
    meta.input_source = "DWD Forecast"

    return meta


def _pull_DWD_historical_data(url: str, station: str) -> pd.DataFrame:
    """
    Ruft die Messdaten von der angegebenen URL ab und konvertiert diese in
    ein pandas DataFrame

    :param url:             str                     URL des DWD-Ordners, in welchem die Messdaten gespeichert sind
    :param station:         int/str                 Stationsname der DWD Wetterstation, Aachen-Orsbach ist 15000
    :return: data           pandas DataFrame        Abgerufener Datensatz und eventuelle Fehlermeldungen
    """

    # First, load all available filenames
    http_obj = urllib.request.urlopen(url).read().decode()

    # select only those file names that belong to the station
    zip_names = [
        i for i in http_obj.split('"') if f"_{station}_" in i and not i.startswith(">")
    ]

    data_total = pd.DataFrame()

    # download and read all available data to df
    for zip_name in zip_names:
        unzipped_path = _download_DWD_file(url, zip_name)

        # extract data file path
        file_name = list(filter(lambda s: s[0] == "p", os.listdir(unzipped_path)))[0]
        file_path = os.path.join(unzipped_path, file_name)

        # read data file
        data = pd.read_csv(file_path, sep=";")

        # unify 10min data with 1h data for "MESS_DATUM" format
        # -> convert 2022012400 to 202201240000
        if len(data.iloc[0]["MESS_DATUM"].astype(str)) == 10:  # if hourly
            data["MESS_DATUM"] = data["MESS_DATUM"] * 100  # add two zeros

        # make MESS_DATUM the index for concenating
        data.set_index("MESS_DATUM", inplace=True, drop=True)

        data_total = pd.concat([data_total, data], verify_integrity=True)

        shutil.rmtree(definitions.local_folder_temp)

    return data_total


def _download_DWD_file(url: str, zip_name: str):
    """
    Downloads the file with the given filename from the specified URL and unzip.

    Parameters:
        url (str): URL of the DWD folder.
        zip_name (str): Name of the file to be downloaded.

    Returns:
        tuple: A tuple containing a boolean indicating the success or failure of the download,
               and the location of the downloaded file.
               Returns (False, None) if an error occurs during download.
    """
    folder_unzip = "unzipped_content"

    total_zip_name = os.path.join(definitions.local_folder_temp, zip_name)

    if not os.path.exists(definitions.local_folder_temp):
        os.makedirs(definitions.local_folder_temp)

    for i in range(4):  # try retrieval 3 times
        try:
            urllib.request.urlretrieve(url + zip_name, total_zip_name)
            print(f"Loaded: {total_zip_name}")

            # save unzipped files to folder_unzip
            extract_path = os.path.join(definitions.local_folder_temp, folder_unzip)
            with zipfile.ZipFile(total_zip_name, "r") as zip_ref:
                zip_ref.extractall(extract_path)

            return extract_path
        except Exception as excep:
            if i == 3:
                raise ConnectionError(
                    f"Not loaded: {total_zip_name} \n" f"with error: {excep}"
                ) from excep
