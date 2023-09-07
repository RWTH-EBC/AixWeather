"""
Change this file to your custom requirements. See the info file in the same
directory for requirements of the returned df.
"""

import pandas as pd

from aixweather import definitions
from aixweather.imports.utils_import import MetaData
from aixweather.transformation_functions import auxiliary, time_observation_transformations, variable_transformations, \
    pass_through_handling, unit_conversions

format_costum = {
    "variable_name_from_your_costum_data": {
        "core_name": "core_name to which it translates (definitions.format_core_data)",
        "time_of_meas_shift": "define if the variable needs to be shifted",
        "unit": "see definitions.format_core_data for naming",
    },
}


def custom_to_core_data(df_import: pd.DataFrame, meta: MetaData) -> pd.DataFrame:
    """
    Converts custom data to core_data
    """
    ### evaluate correctness of format
    auxiliary.evaluate_transformations(
        core_format=definitions.format_core_data, other_format=format_costum
    )

    ### preprocessing raw data for further operations
    df = df_import.copy()
    # rename available variables to core data format
    df = auxiliary.rename_columns(df, format_costum)

    ### convert timezone to UTC+0 -> change periods accordingly
    df = df.shift(periods=0, freq="H", axis=0)

    ### shift and interpolate data forward 30mins or backward -30mins
    df_no_shift = df.copy()
    df = time_observation_transformations.shift_time_by_dict(
        format_costum, df
    )

    def transform_custom(df):
        # drop unnecessary variables
        df = auxiliary.force_data_variable_convention(df, definitions.format_core_data)

        ### convert units
        # insert unit conversions like desired (examples follow)
        df["TotalSkyCover"] = unit_conversions.eigth_to_tenth(df["TotalSkyCover"])
        df["AtmPressure"] = unit_conversions.hPa_to_Pa(df["AtmPressure"])

        ### impute missing variables from other available ones
        # add additionaly required transformations to
        # variable_transformations.variable_transform_all or apply them directly here
        df, calc_overview = variable_transformations.variable_transform_all(df, meta)
        return df, calc_overview

    df, meta.executed_transformations = transform_custom(df)

    ### add unshifted data for possible later direct use (pass-through),
    ### to avoid back and forth interpolating
    df = pass_through_handling.create_pass_through_variables(
        df_shifted=df,
        df_no_shift=df_no_shift,
        format=format_costum,
        transform_func=transform_custom,
        meta=meta,
    )

    return df
