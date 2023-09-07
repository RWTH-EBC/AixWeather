import pandas as pd

from aixweather.imports.utils_import import MetaData
from aixweather.transformation_functions import auxiliary, time_observation_transformations, variable_transformations, \
    pass_through_handling, unit_conversions

"""
format_TRY_15_45 information 

checked by Martin Rätz (08.08.2023)
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
        core_format=auxiliary.format_core_data, other_format=format_TRY_15_45
    )

    ### preprocessing raw data for further operations
    df = df_import.copy()
    # rename available variables to core data format
    df = auxiliary.rename_columns(df, format_TRY_15_45)

    ### convert timezone to UTC+0
    df = df.shift(periods=-1, freq="H", axis=0)

    ### shift and interpolate data forward 30mins or backward -30mins
    df_no_shift = df.copy()
    df = time_observation_transformations.shift_time_by_dict(format_TRY_15_45, df)

    def transform_TRY(df):
        # drop unnecessary variables
        df = auxiliary.force_data_variable_convention(df, auxiliary.format_core_data)
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
