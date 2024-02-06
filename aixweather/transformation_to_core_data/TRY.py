import pandas as pd
import datetime as dt

from aixweather import definitions
from aixweather.imports.utils_import import MetaData
from aixweather.transformation_functions import auxiliary, time_observation_transformations, variable_transformations, \
    pass_through_handling, unit_conversions

"""
format_TRY_15_45 information 

Format info:
key = raw data point name
core_name = corresponding name matching the format_core_data
time_of_meas_shift = desired 30min shifting+interpolation to convert a value that is e.g. the 
"average of preceding hour" to "indicated time" (prec2ind). 
unit = unit of the raw data following the naming convention of format_core_data

All changes here automatically change the calculations. 
Exception: unit conversions have to be added manually.

checked by Martin Rätz (08.08.2023)

https://www.bbsr.bund.de/BBSR/DE/forschung/programme/zb/Auftragsforschung/5EnergieKlimaBauen/2013/testreferenzjahre/try-handbuch.pdf;jsessionid=9F928CDB6862224B04073332C2B1B620.live21301?__blob=publicationFile&v=1
Der erste Eintrag im Datensatz bezieht sich auf den 1. Januar 01 Uhr MEZ und
der letzte Eintrag auf den 31. Dezember 24 Uhr MEZ. Also UTC+1.
"""
format_TRY_15_45 = {
    "t": {"core_name": "DryBulbTemp", "time_of_meas_shift": "prec2ind", "unit": "degC"},
    "p": {"core_name": "AtmPressure", "time_of_meas_shift": None, "unit": "hPa"},
    "WR": {"core_name": "WindDir", "time_of_meas_shift": None, "unit": "deg"},
    "WG": {"core_name": "WindSpeed", "time_of_meas_shift": None, "unit": "m/s"},
    "N": {"core_name": "TotalSkyCover", "time_of_meas_shift": None, "unit": "1eigth"},
    # 'x',
    "RF": {"core_name": "RelHum", "time_of_meas_shift": "prec2ind", "unit": "percent"},
    "B": {"core_name": "DirHorRad", "time_of_meas_shift": "prec2ind", "unit": "Wh/m2"},
    "D": {"core_name": "DiffHorRad", "time_of_meas_shift": "prec2ind", "unit": "Wh/m2"},
    "A": {"core_name": "HorInfra", "time_of_meas_shift": None, "unit": "Wh/m2"},
    # 'E',
}


def TRY_to_core_data(df_import: pd.DataFrame, meta: MetaData) -> pd.DataFrame:
    """
    Transform imported TRY data of the formats 2015 and 2045 into the core data format.

    Args:
        df_import (pd.DataFrame): The DataFrame containing imported TRY weather data.
        meta (MetaData): Metadata associated with the data.

    Returns:
        pd.DataFrame: The transformed DataFrame in the core data format.
    """

    ### evaluate correctness of format
    auxiliary.evaluate_transformations(
        core_format=definitions.format_core_data, other_format=format_TRY_15_45
    )

    def TRY_to_datetimeindex(df, meta: MetaData):
        # set index to datetime
        # returns datetime objects
        df["MM"] = df["MM"].astype(int)
        df["DD"] = df["DD"].astype(int)
        df["HH"] = df["HH"].astype(int)
        time_index = df.apply(
            lambda row: dt.datetime(int(meta.try_year), row.MM, row.DD, row.HH - int(1.0)),
            axis=1,
        )
        # data is shifted by -1 H to satisfy pandas timestamp
        # hours in pandas only between 0 and 23, in TRY between 1 and 24
        # converts to pandas timestamps if desired
        df.index = pd.to_datetime(time_index)
        # data is shifted back to original to start: back to
        # 2017-01-01 01:00:00 instead of the temporary 2017-01-01 00:00:00
        df = df.shift(periods=1, freq="H", axis=0)

        return df

    ### preprocessing raw data for further operations
    df = df_import.copy()
    df = TRY_to_datetimeindex(df, meta)
    # Resample the DataFrame to make the DatetimeIndex complete and monotonic
    df = df.resample('H').asfreq()
    # rename available variables to core data format
    df = auxiliary.rename_columns(df, format_TRY_15_45)

    ### convert timezone to UTC+0
    df = df.shift(periods=-1, freq="H", axis=0)

    ### shift and interpolate data forward 30mins or backward -30mins
    df_no_shift = df.copy()
    df = time_observation_transformations.shift_time_by_dict(format_TRY_15_45, df)

    def transform_TRY(df):
        # drop unnecessary variables
        df = auxiliary.force_data_variable_convention(df, definitions.format_core_data)
        ### convert units
        df["TotalSkyCover"] = unit_conversions.eigth_to_tenth(df["TotalSkyCover"])
        df["AtmPressure"] = unit_conversions.hPa_to_Pa(df["AtmPressure"])
        ### impute missing variables from other available ones
        df, calc_overview = variable_transformations.variable_transform_all(df, meta)
        return df, calc_overview

    df, meta.executed_transformations = transform_TRY(df)

    ### add unshifted data for possible later direct use (pass-through),
    ### to avoid back and forth interpolating
    df = pass_through_handling.create_pass_through_variables(
        df_shifted=df,
        df_no_shift=df_no_shift,
        format=format_TRY_15_45,
        transform_func=transform_TRY,
        meta=meta,
    )

    return df
