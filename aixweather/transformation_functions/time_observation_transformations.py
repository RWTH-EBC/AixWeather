"""
Includes functions to execute time shift operations. It also includes a
function to truncate data in given interval.
"""

import datetime
import logging

import pandas as pd


logger = logging.getLogger(__name__)


def _shift_timestamps_and_interpolate(df: pd.DataFrame, backward: bool) -> pd.DataFrame:
    """
    Shift and interpolate timestamps in a DataFrame by 30 minutes forward or backward.

    This function shifts and interpolates the timestamps in the DataFrame `df` by either
    30 minutes forward or backward based on the `backward` parameter. It uses linear interpolation
    to fill in missing values during the shift.

    Args:
        df (pd.DataFrame): The DataFrame containing timestamped data.
        backward (bool): If True, shift timestamps 30 minutes backward. If False, shift them 30 minutes forward.

    Returns:
        pd.DataFrame: A DataFrame with timestamps shifted and interpolated as specified.
    """

    if (
        backward
    ):  # avg_preceding_hour_2_indicated_time or indicated_time_2_avg_following_hour
        interval = "-30min"
    else:  # avg_following_hour_2_indicated_time or indicated_time_2_avg_preceding_hour
        interval = "30min"
    df = df.astype(float)

    # shift and interpolate
    df_shifted = df.shift(freq=interval)
    df_interpolated = df_shifted.resample("30min").interpolate(method="linear", limit=1)

    # keep only original timestamps
    df_final = df_interpolated.reindex(df.index)

    return df_final


def avg_preceding_hour_2_indicated_time(df):
    '''aka: prec2ind'''
    return _shift_timestamps_and_interpolate(df, True)


def indicated_time_2_avg_following_hour(df):
    '''aka: ind2foll'''
    return _shift_timestamps_and_interpolate(df, True)


def avg_following_hour_2_indicated_time(df):
    '''aka: foll2ind'''
    return _shift_timestamps_and_interpolate(df, False)


def indicated_time_2_avg_preceding_hour(df):
    '''aka: ind2prec'''
    return _shift_timestamps_and_interpolate(df, False)


def shift_time_by_dict(format_dict: dict, df: pd.DataFrame) -> pd.DataFrame:
    """
    Shift timestamps in a DataFrame based on a format dictionary.

    This function shifts and interpolates values in the DataFrame `df` based on the specified format dictionary. The format
    dictionary should contain information about the desired time shifting for core data variables.

    Args:
        format_dict (dict): A dictionary specifying the time shifting for core data variables.
        df (pd.DataFrame): The DataFrame containing timestamped data with core data variable names.

    Returns:
        pd.DataFrame: The modified DataFrame with values shifted and interpolated according to the format dictionary.
    """
    meas_key = "time_of_meas_shift"
    core_name = "core_name"
    for key, value in format_dict.items():
        # No measurement if not present, though avoid being triggered
        # when using this function in 2output (empty string)
        if value[core_name] not in df.columns and value[core_name]:
            logger.info("No measurements for %s.", value[core_name])
        else:
            if value[meas_key] == "prec2ind":
                df.loc[:, value[core_name]] = avg_preceding_hour_2_indicated_time(
                    df[value[core_name]]
                )
            elif value[meas_key] == "ind2foll":
                df.loc[:, value[core_name]] = indicated_time_2_avg_following_hour(
                    df[value[core_name]]
                )
            elif value[meas_key] == "foll2ind":
                df.loc[:, value[core_name]] = avg_following_hour_2_indicated_time(
                    df[value[core_name]]
                )
            elif value[meas_key] == "ind2prec":
                df.loc[:, value[core_name]] = indicated_time_2_avg_preceding_hour(
                    df[value[core_name]]
                )
            elif value[meas_key] is None:
                pass
            else:
                raise ValueError(
                    f"Invalid keyword for {meas_key} for {key}: '{value[meas_key]}' is not valid."
                )
    return df


def truncate_data_from_start_to_stop(
    df: pd.DataFrame, start: datetime, stop: datetime
) -> pd.DataFrame:
    """
    Truncate a DataFrame to include data only between specified start and stop timestamps.

    Args:
        df (pd.DataFrame): The DataFrame containing timestamped data.
        start (datetime): The start timestamp to include in the truncated DataFrame.
        stop (datetime): The stop timestamp to include in the truncated DataFrame.

    Returns:
        pd.DataFrame: A new DataFrame containing data only within the specified time range.
    """
    mask = (df.index >= start) & (df.index <= stop)
    df = df.loc[mask]
    return df
