"""
This module includes a function to transform EPW data to core data format.
"""

import pandas as pd
from copy import deepcopy

from aixweather import definitions
from aixweather.imports.utils_import import MetaData
from aixweather.transformation_functions import (
    auxiliary,
    time_observation_transformations,
    variable_transformations,
    pass_through_handling,
)
from aixweather.core_data_format_2_output_file.to_epw_energyplus import (
    format_epw as format_epw_export,
)


def EPW_to_core_data(df_import: pd.DataFrame, meta: MetaData) -> pd.DataFrame:
    """
    Transform imported EPW (EnergyPlus Weather) data into core data format.

    Args:
        df_import (pd.DataFrame): The DataFrame containing imported EPW weather data.
        meta (MetaData): Metadata associated with the data.

    Returns:
        pd.DataFrame: The transformed DataFrame in the core data format.
    """

    # invert format_epw from core2export to import2core
    format_epw = deepcopy(format_epw_export)
    for key, value in format_epw.items():
        time_shift = value["time_of_meas_shift"]
        if time_shift == "ind2prec":
            value["time_of_meas_shift"] = "prec2ind"
        elif time_shift == "ind2foll":
            value["time_of_meas_shift"] = "foll2ind"

    # evaluate correctness of format
    auxiliary.evaluate_transformations(
        core_format=definitions.format_core_data, other_format=format_epw
    )

    ### preprocessing raw data for further operations
    df = df_import.copy()
    # give names to columns according to documentation of import data
    df.columns = [key for key in format_epw.keys()]
    # rename available variables to core data format
    df = auxiliary.rename_columns(df, format_epw)
    # delete dummy values from EPW
    df = auxiliary.replace_dummy_with_nan(df, format_epw)

    ### convert timezone to UTC+0
    df = df.shift(periods=meta.timezone, freq="H", axis=0)

    ### shift and interpolate data forward 30mins or backward -30mins
    df_no_shift = df.copy()
    df = time_observation_transformations.shift_time_by_dict(format_epw, df)

    def transform(df):
        ### force variable naming format_core_data
        df = auxiliary.force_data_variable_convention(df, definitions.format_core_data)
        ### unit conversion
        # all units correct
        ### impute missing variables from other available ones
        df, calc_overview = variable_transformations.variable_transform_all(df, meta)
        return df, calc_overview

    df, meta.executed_transformations = transform(df)

    ### add unshifted data for possible later direct use (pass-through),
    ### to avoid back and forth interpolating
    df = pass_through_handling.create_pass_through_variables(
        df_shifted=df,
        df_no_shift=df_no_shift,
        format=format_epw,
        transform_func=transform,
        meta=meta,
    )

    return df
