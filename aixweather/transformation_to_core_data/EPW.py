"""
This module includes a function to transform EPW data to core data format.
"""

import pandas as pd
from copy import deepcopy
import logging

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

logger = logging.getLogger(__name__)


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

    def epw_to_datetimeindex(df):
        '''
        Convert the first 4 columns of the DataFrame to a DatetimeIndex and set it as the
        index.'''
        # The first 4 columns represent year, month, day, and hour respectively,
        # but with hour 24 instead of hour 0.
        hour = df.iloc[:, 3].copy()
        mask_24hr = hour == 24
        hour.loc[mask_24hr] = 0

        # loop one by one to avoid faults with non-continuous data
        datetime_list = []
        for index, row in df.iterrows():
            year, month, day, hour = row[:4]
            if hour == 24:
                hour = 0
                # Increment the day by one for those rows where hour
                # was originally 24
                row_datetime = pd.Timestamp(year, month, day, hour) + pd.Timedelta(days=1)
            else:
                row_datetime = pd.Timestamp(year, month, day, hour)
            datetime_list.append(row_datetime)

        # Setting datetime column as index with name 'datetime'
        df.index = datetime_list
        df.index = df.index.rename('datetime')

        return df

    def if_TMY_convert_to_one_year(df):
        """TMY (typical meteorological year) data in .epw files often contains data for a period
        of one year but each month is from a different year. This will lead to several years of
        nan data in between. As the year is irrelevant in tmy data, we set all dates to the year
        of februaries data. February is chosen to avoid leap year issues.

        It is automatically detected whether it is a TMY through the following criteria:
        - the available data covers exactly 8760 data points (one non-leap year)
        - the period covered by the timestamps spans more than one year
        - the first date is the first of January at hour 1

        This will lead to an info log message if the data is transformed."""
        if (
            len(df) == 8760 # exactly one year of data
            and df.iloc[:, 0].max() - df.iloc[:, 0].min() > 1 # spanning over more than one year
            and df.iloc[0, 1] == 1 # first month is January
            and df.iloc[0, 2] == 1 # first day is one
            and df.iloc[0, 3] == 1 # first hour is one
        ):
            year_of_february = df.loc[df.iloc[:, 1] == 2, 0].iloc[0]
            # Replace the year component with the year of February
            df.iloc[:, 0] = year_of_february
            logger.info(
                "The data was transformed to one year of data as it seems to be TMY data."
                "The year is irrelevant for TMY data."
            )
        return df

    ### preprocessing raw data for further operations
    df = df_import.copy()
    df = if_TMY_convert_to_one_year(df)
    df = epw_to_datetimeindex(df)
    # Resample the DataFrame to make the DatetimeIndex complete and monotonic
    df = df.resample("H").asfreq()
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
