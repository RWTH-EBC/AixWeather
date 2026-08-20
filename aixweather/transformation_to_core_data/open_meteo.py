"""
This module includes functions to transform Open-Meteo data to core data format.
"""

import pandas as pd

from aixweather import definitions
from aixweather.imports.utils_import import MetaData
from aixweather.transformation_functions import (
    auxiliary,
    time_observation_transformations,
    variable_transformations,
    pass_through_handling,
    unit_conversions,
)


class OpenMeteoHistoricalFormat:
    """
    Information on the Open-Meteo historical (archive) data:
    https://open-meteo.com/en/docs/historical-weather-api

    The historical data is reanalysis data (ERA5 and ERA5-Land), i.e. no measurements
    of a weather station but the best estimate of a grid point.

    Format info:
    key = raw data point name
    core_name = corresponding name matching the format_core_data
    time_of_meas_shift = desired 30min shifting+interpolation to convert a value that is e.g. the
    "average of preceding hour" to "indicated time" (prec2ind).
    unit = unit of the raw data following the naming convention of format_core_data
    nan = values or value ranges that are considered as missing values

    All changes here automatically change the calculations.
    Exception: unit conversions have to be added manually.

    Time of measurement and units as documented by Open-Meteo:
    all variables are valid for the indicated time, except the radiation and the
    precipitation, which are the mean respectively the sum of the preceding hour.
    """

    @classmethod
    def import_format(cls) -> dict:
        return {
            "temperature_2m": {"core_name": "DryBulbTemp", "time_of_meas_shift": None, "unit": "degC"},
            "relative_humidity_2m": {"core_name": "RelHum", "time_of_meas_shift": None, "unit": "percent", "nan": [{"<": 0}, {">": 100}]},
            "dew_point_2m": {"core_name": "DewPointTemp", "time_of_meas_shift": None, "unit": "degC"},
            "surface_pressure": {"core_name": "AtmPressure", "time_of_meas_shift": None, "unit": "hPa", "nan": [{"<": 0}]},
            "cloud_cover": {"core_name": "TotalSkyCover", "time_of_meas_shift": None, "unit": "percent", "nan": [{"<": 0}, {">": 100}]},
            "wind_speed_10m": {"core_name": "WindSpeed", "time_of_meas_shift": None, "unit": "m/s", "nan": [{"<": 0}]},
            "wind_direction_10m": {"core_name": "WindDir", "time_of_meas_shift": None, "unit": "deg", "nan": [{"<": 0}, {">": 360}]},
            "shortwave_radiation": {"core_name": "GlobHorRad", "time_of_meas_shift": "prec2ind", "unit": "W/m2", "nan": [{"<": 0}]},
            "diffuse_radiation": {"core_name": "DiffHorRad", "time_of_meas_shift": "prec2ind", "unit": "W/m2", "nan": [{"<": 0}]},
            "direct_radiation": {"core_name": "DirHorRad", "time_of_meas_shift": "prec2ind", "unit": "W/m2", "nan": [{"<": 0}]},
            "direct_normal_irradiance": {"core_name": "DirNormRad", "time_of_meas_shift": "prec2ind", "unit": "W/m2", "nan": [{"<": 0}]},
            # radiation at the top of the atmosphere on a horizontal plane
            "terrestrial_radiation": {"core_name": "ExtHorRad", "time_of_meas_shift": "prec2ind", "unit": "W/m2", "nan": [{"<": 0}]},
            # sum of the preceding hour in mm, which equals mm/h
            "precipitation": {"core_name": "LiquidPrecD", "time_of_meas_shift": "prec2ind", "unit": "mm/h", "nan": [{"<": 0}]},
            # ERA5 provides soil temperatures as average of a soil layer. They are
            # assigned to the core variable of the closest depth. Deeper layers
            # (28 to 100cm and 100 to 255cm) are not pulled, as their layers are too
            # thick to be assigned to a core variable.
            "soil_temperature_0_to_7cm": {"core_name": "Soil_Temperature_5cm", "time_of_meas_shift": None, "unit": "degC"},
            "soil_temperature_7_to_28cm": {"core_name": "Soil_Temperature_20cm", "time_of_meas_shift": None, "unit": "degC"},
        }


class OpenMeteoForecastFormat:
    """
    Information on the Open-Meteo forecast data: https://open-meteo.com/en/docs

    Open-Meteo combines the forecasts of several weather models to a forecast for the
    grid point closest to the requested coordinates.

    For the format info see OpenMeteoHistoricalFormat.

    Compared to the historical data, the forecast additionally provides the visibility
    and uses other soil depths.
    """

    @classmethod
    def import_format(cls) -> dict:
        format_dict = OpenMeteoHistoricalFormat.import_format()

        # soil temperatures are given for other depths than in the historical data,
        # they are assigned to the core variable of the closest depth
        del format_dict["soil_temperature_0_to_7cm"]
        del format_dict["soil_temperature_7_to_28cm"]

        format_dict.update(
            {
                "visibility": {"core_name": "Visibility", "time_of_meas_shift": None, "unit": "m", "nan": [{"<": 0}]},
                "soil_temperature_6cm": {"core_name": "Soil_Temperature_5cm", "time_of_meas_shift": None, "unit": "degC"},
                "soil_temperature_18cm": {"core_name": "Soil_Temperature_20cm", "time_of_meas_shift": None, "unit": "degC"},
                "soil_temperature_54cm": {"core_name": "Soil_Temperature_50cm", "time_of_meas_shift": None, "unit": "degC"},
            }
        )

        return format_dict


def open_meteo_historical_to_core_data(
    df_import: pd.DataFrame, meta: MetaData
) -> pd.DataFrame:
    """
    Transform imported historical weather data from Open-Meteo into core data format.

    Args:
        df_import (pd.DataFrame): The DataFrame containing imported weather data from Open-Meteo.
        meta (MetaData): Metadata associated with the data.

    Returns:
        pd.DataFrame: The transformed DataFrame in the core data format.
    """
    return _open_meteo_to_core_data(
        df_import=df_import,
        meta=meta,
        format_open_meteo=OpenMeteoHistoricalFormat.import_format(),
    )


def open_meteo_forecast_to_core_data(
    df_import: pd.DataFrame, meta: MetaData
) -> pd.DataFrame:
    """
    Transform imported weather forecast data from Open-Meteo into core data format.

    Args:
        df_import (pd.DataFrame): The DataFrame containing imported weather forecast data
            from Open-Meteo.
        meta (MetaData): Metadata associated with the data.

    Returns:
        pd.DataFrame: The transformed DataFrame in the core data format.
    """
    return _open_meteo_to_core_data(
        df_import=df_import,
        meta=meta,
        format_open_meteo=OpenMeteoForecastFormat.import_format(),
    )


def _open_meteo_to_core_data(
    df_import: pd.DataFrame, meta: MetaData, format_open_meteo: dict
) -> pd.DataFrame:
    """
    Transform imported Open-Meteo data into core data format. The historical and the
    forecast data only differ in their format dictionary.

    Args:
        df_import (pd.DataFrame): The DataFrame containing imported weather data from Open-Meteo.
        meta (MetaData): Metadata associated with the data.
        format_open_meteo (dict): The format of the imported data.

    Returns:
        pd.DataFrame: The transformed DataFrame in the core data format.
    """

    ### evaluate correctness of format
    auxiliary.evaluate_transformations(
        core_format=definitions.format_core_data, other_format=format_open_meteo
    )

    ### format raw data for further operations
    df = df_import.copy()
    df.index = pd.to_datetime(df.index)
    # variables that are entirely missing are returned as strings by the API
    df = df.apply(pd.to_numeric, errors="coerce")
    # make the DatetimeIndex complete and monotonic
    df = df.sort_index().resample("h").asfreq()
    # delete implausible values
    df = auxiliary.replace_dummy_with_nan(df, format_open_meteo)
    # rename available variables to core data format
    df = auxiliary.rename_columns(df, format_open_meteo)

    ### convert timezone to UTC
    # the data is pulled in UTC (timezone=GMT), see aixweather.imports.open_meteo

    ### shift and interpolate data forward 30mins or backward -30mins
    df_no_shift = df.copy()
    df = time_observation_transformations.shift_time_by_dict(format_open_meteo, df)

    def transform_open_meteo(df):
        # drop unnecessary variables
        df = auxiliary.force_data_variable_convention(df, definitions.format_core_data)

        ### convert units
        df["AtmPressure"] = unit_conversions.hPa_to_Pa(df["AtmPressure"])
        df["TotalSkyCover"] = unit_conversions.percent_to_tenth(df["TotalSkyCover"])
        df["ExtHorRad"] = unit_conversions.Wm2_to_Whm2(df["ExtHorRad"])
        df["GlobHorRad"] = unit_conversions.Wm2_to_Whm2(df["GlobHorRad"])
        df["DirHorRad"] = unit_conversions.Wm2_to_Whm2(df["DirHorRad"])
        df["DirNormRad"] = unit_conversions.Wm2_to_Whm2(df["DirNormRad"])
        df["DiffHorRad"] = unit_conversions.Wm2_to_Whm2(df["DiffHorRad"])
        # only given by the forecast data, nan otherwise
        df["Visibility"] = unit_conversions.divide_by_1000(df["Visibility"])

        ### impute missing variables from other available ones
        df, calc_overview = variable_transformations.variable_transform_all(df, meta)

        return df, calc_overview

    df, meta.executed_transformations = transform_open_meteo(df)

    ### add unshifted data for possible later direct use (pass-through),
    ### to avoid back and forth interpolating
    df = pass_through_handling.create_pass_through_variables(
        df_shifted=df,
        df_no_shift=df_no_shift,
        format=format_open_meteo,
        transform_func=transform_open_meteo,
        meta=meta,
    )

    return df
