"""
Includes functions to execute time shift operations. It also includes a
function to truncate data in given interval.
"""

import datetime
import pandas as pd


def _shift_timestamps_and_interpolate(df, backward: bool):
    """
    shift (and interpolate) data by 30 min or -30 min
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
    df_interpolated = df_shifted.resample("30min").interpolate(method="linear")

    # keep only original timestamps
    df_final = df_interpolated.reindex(df.index)

    return df_final


def avg_preceding_hour_2_indicated_time(df):
    return _shift_timestamps_and_interpolate(df, True)


def indicated_time_2_avg_following_hour(df):
    return _shift_timestamps_and_interpolate(df, True)


def avg_following_hour_2_indicated_time(df):
    return _shift_timestamps_and_interpolate(df, False)


def indicated_time_2_avg_preceding_hour(df):
    return _shift_timestamps_and_interpolate(df, False)


def shift_time_by_dict(format_dict: dict, df: pd.DataFrame):
    """
    df : must be with core data variable names to work correct
    """
    meas_key = "time_of_meas_shift"
    core_name = "core_name"
    for key, value in format_dict.items():
        # No measurement if not present, though avoid being triggered
        # when using this function in 2output (empty string)
        if value[core_name] not in df.columns and value[core_name]:
            print(f"No measurements for {value[core_name]}.")
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
    df: pd.DataFrame, start: datetime, stop: "datetime"
):
    """
    filter df to start and stop
    """
    mask = (df.index >= start) & (df.index <= stop)
    df = df.loc[mask]
    return df
