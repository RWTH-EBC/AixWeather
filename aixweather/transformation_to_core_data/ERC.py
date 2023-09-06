"""
This module includes functions to transform ERC data to core data format.
"""

import pandas as pd

from aixweather.imports.utils_import import MetaData
from aixweather.transformation_functions import auxiliary, time_observation_transformations, variable_transformations, \
    pass_through_handling, unit_conversions

"""
format_ERC information

checked by Martin Rätz 01.09.2023
"""
format_ERC = {
    '4121.weatherstation.temperature': {'core_name': 'DryBulbTemp', 'time_of_meas_shift': 'foll2ind', 'unit': "degC"},
    '4121.weatherstation.diffuse-radiation': {'core_name': 'DiffHorRad', 'time_of_meas_shift': 'foll2ind', 'unit': "Wh/m2"},
    '4121.weatherstation.global-radiation': {'core_name': 'GlobHorRad', 'time_of_meas_shift': 'foll2ind', 'unit': "Wh/m2"},
    '4121.weatherstation.pressure': {'core_name': 'AtmPressure', 'time_of_meas_shift': 'foll2ind', 'unit': "hPa"},
    '4121.weatherstation.relative-humidity': {'core_name': 'RelHum', 'time_of_meas_shift': 'foll2ind', 'unit': "percent"},
    '4121.weatherstation.wind-direction': {'core_name': 'WindDir', 'time_of_meas_shift': 'foll2ind', 'unit': "deg"},
    '4121.weatherstation.wind-speed': {'core_name': 'WindSpeed', 'time_of_meas_shift': 'foll2ind', 'unit': "m/s"},
    # too little information available, also possibly needs a sum up not a mean when interpolating
    # 'rainfall': {'core_name': 'PrecWater',
    # 'time_of_meas_shift': 'foll2ind',
    # 'unit': "mm/h"}
}


def ERC_to_core_data(df_import: pd.DataFrame, meta: MetaData) -> pd.DataFrame:
    """
    Transform imported ERC (Energy Research Center) weather data into core data format.

    Args:
        df_import (pd.DataFrame): The DataFrame containing imported ERC weather data.
        meta (MetaData): Metadata associated with the data.

    Returns:
        pd.DataFrame: The transformed DataFrame in the core data format.
    """

    ### evaluate correctness of format
    auxiliary.evaluate_transformations(
        core_format=auxiliary.format_core_data, other_format=format_ERC
    )

    ### format raw data for further operations
    df = df_import.copy()

    # Remove timezone awareness
    df.index = df.index.tz_localize(None)

    # rename available variables to core data format
    df = auxiliary.rename_columns(df, format_ERC)

    ### convert timezone to UTC
    # data is UTC

    ### shift and interpolate data forward 30mins or backward -30mins
    df_no_shift = df.copy()
    df = time_observation_transformations.shift_time_by_dict(format_ERC, df)

    def transform_ERC(df):
        # drop unnecessary variables
        df = auxiliary.force_data_variable_convention(df, auxiliary.format_core_data)

        ### convert units
        df["AtmPressure"] = unit_conversions.hPa_to_Pa(df["AtmPressure"])

        ### impute missing variables from other available ones
        df, calc_overview = variable_transformations.variable_transform_all(df, meta)

        return df, calc_overview

    df, meta.executed_transformations = transform_ERC(df)

    ### add unshifted data for possible later direct use (pass-through),
    ### to avoid back and forth interpolating
    df = pass_through_handling.create_pass_through_variables(
        df_shifted=df,
        df_no_shift=df_no_shift,
        format=format_ERC,
        transform_func=transform_ERC,
        meta=meta,
    )

    return df
