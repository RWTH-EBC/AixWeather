from datetime import datetime, timedelta
import pandas as pd

from aixweather import definitions
from aixweather.imports.utils_import import MetaData
from aixweather.transformation_functions import auxiliary, time_observation_transformations, variable_transformations, \
    pass_through_handling, unit_conversions

"""
format_DWD_historical information:
see readme

Format info:
key = raw data point name
core_name = corresponding name matching the format_core_data
time_of_meas_shift = desired 30min shifting+interpolation to convert a value that is e.g. the 
"average of preceding hour" to "indicated time" (prec2ind). 
unit = unit of the raw data following the naming convention of format_core_data

All changes here automatically change the calculations. 
Exception: unit conversions have to be added manually.

checked by Martin Rätz (08.08.2023)
"""
format_DWD_historical = {
    # https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/
    # 10_minutes/air_temperature/DESCRIPTION_obsgermany_climate_10min_air_temperature_en.pdf
    "RF_10": {"core_name": "RelHum", "time_of_meas_shift": "foll2ind", "unit": "percent"},
    "TT_10": {"core_name": "DryBulbTemp", "time_of_meas_shift": "foll2ind", "unit": "degC"},
    "TD_10": {"core_name": "DewPointTemp", "time_of_meas_shift": "foll2ind", "unit": "degC"},
    "PP_10": {"core_name": "AtmPressure", "time_of_meas_shift": "foll2ind", "unit": "hPa"},
    #https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/10_minutes/solar/BESCHREIBUNG_obsgermany_climate_10min_solar_de.pdf
    "DS_10": {"core_name": "DiffHorRad", "time_of_meas_shift": "foll2ind", "unit": "J/cm2", "resample": "sum"},
    #https://de.wikipedia.org/wiki/Globalstrahlung
    "GS_10": {"core_name": "GlobHorRad", "time_of_meas_shift": "foll2ind", "unit": "J/cm2", "resample": "sum"},
    #https://de.wikipedia.org/wiki/Atmosph%C3%A4rische_Gegenstrahlung
    "LS_10": {"core_name": "HorInfra", "time_of_meas_shift": "foll2ind", "unit": "J/cm2", "resample": "sum", "nan":[990, -999]},
    #https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/10_minutes/wind/BESCHREIBUNG_obsgermany_climate_10min_wind_de.pdf
    "FF_10": {"core_name": "WindSpeed", "time_of_meas_shift": "prec2ind", "unit": "m/s"},
    "DD_10": {"core_name": "WindDir", "time_of_meas_shift": "prec2ind", "unit": "deg"},
    # https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/10_minutes/precipitation/BESCHREIBUNG_obsgermany_climate_10min_precipitation_de.pdf
    "RWS_10": {"core_name": "LiquidPrecD", "time_of_meas_shift": "prec2ind", "unit": "mm/h", "resample": "sum"},
    # https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/soil_temperature/BESCHREIBUNG_obsgermany_climate_hourly_soil_temperature_de.pdf
    "V_TE100": {"core_name": "Soil_Temperature_1m", "time_of_meas_shift": None, "unit": "degC"},
    "V_TE050": {"core_name": "Soil_Temperature_50cm", "time_of_meas_shift": None, "unit": "degC"},
    "V_TE020": {"core_name": "Soil_Temperature_20cm", "time_of_meas_shift": None, "unit": "degC"},
    "V_TE010": {"core_name": "Soil_Temperature_10cm", "time_of_meas_shift": None, "unit": "degC"},
    "V_TE005": {"core_name": "Soil_Temperature_5cm", "time_of_meas_shift": None, "unit": "degC"},
    # https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/cloud_type/BESCHREIBUNG_obsgermany_climate_hourly_cloud_type_de.pdf
    " V_N": {"core_name": "TotalSkyCover", "time_of_meas_shift": None, "unit": "1eighth"},
    # Hourly measurements currently unused due to doubling with 10
    # minute data and conflicting time shifting and units
    # "RF_TU": "RelHum",
    # "TT_TU": "DryBulbTemp",
    # "  P0": "AtmPressure",
    # "   P": "Pressure_Sea_Level",
    # "   F": "WindSpeed",
    # "   D": "WindDir",
    # "  R1": "LiquidPrecD",
}
# get variables that should be resampled by sum instead of mean
variables_to_sum_DWD_historical = [
    key for key, value in format_DWD_historical.items() if "resample" in value.keys()
]

"""
format_DWD_forecast information:

Variable definitions: https://opendata.dwd.de/weather/lib/MetElementDefinition.xml or 
https://wetterdienst.readthedocs.io/en/latest/data/coverage/dwd/mosmix/hourly.html (in origin unit)

checked by Martin Rätz 18.08.2023
"""
format_DWD_forecast = {
    # "cloud_cover_above_7_km": None,
    # "cloud_cover_below_1000_ft": None,
    # "cloud_cover_below_500_ft": None,
    # "cloud_cover_between_2_to_7_km": None,
    "cloud_cover_effective": {"core_name": "OpaqueSkyCover", "time_of_meas_shift": None, "unit": "%"},
    "cloud_cover_total": {"core_name": "TotalSkyCover", "time_of_meas_shift": None, "unit": "%"},
    # "precipitation_height_significant_weather_last_1h": None,
    # "precipitation_height_significant_weather_last_3h": None,
    "pressure_air_site_reduced": {"core_name": "AtmPressure", "time_of_meas_shift": None, "unit": "Pa"},
    # "probability_fog_last_12h": None,
    # "probability_fog_last_1h": None,
    # "probability_fog_last_6h": None,
    # "probability_precipitation_height_gt_0_0_mm_last_12h": None,
    # "probability_precipitation_height_gt_0_2_mm_last_12h": None,
    # "probability_precipitation_height_gt_0_2_mm_last_24h": None,
    # "probability_precipitation_height_gt_0_2_mm_last_6h": None,
    # "probability_precipitation_height_gt_1_0_mm_last_12h": None,
    # "probability_precipitation_height_gt_5_0_mm_last_12h": None,
    # "probability_precipitation_height_gt_5_0_mm_last_24h": None,
    # "probability_precipitation_height_gt_5_0_mm_last_6h": None,
    # "probability_wind_gust_ge_25_kn_last_12h": None,
    # "probability_wind_gust_ge_40_kn_last_12h": None,
    # "probability_wind_gust_ge_55_kn_last_12h": None,
    # is actually balance during the last 3 hours:
    "radiation_global": {"core_name": "GlobHorRad", "time_of_meas_shift": "prec2ind", "unit": "kJ/m2"},
    # "sunshine_duration": None,
    # "temperature_air_max_200": None,
    # "temperature_air_mean_005": None,
    # no information if temperature is drybulb or something else:
    "temperature_air_mean_200": {"core_name": "DryBulbTemp", "time_of_meas_shift": None, "unit": "K"},
    # "temperature_air_min_200": None,
    "temperature_dew_point_mean_200": {"core_name": "DewPointTemp", "time_of_meas_shift": None, "unit": "K"},
    "visibility_range": {"core_name": "Visibility", "time_of_meas_shift": None, "unit": "m"},
    # "water_equivalent_snow_depth_new_last_1h": None,
    # "water_equivalent_snow_depth_new_last_3h": None,
    # "weather_last_6h": None,
    # "weather_significant": None,
    "wind_direction": {"core_name": "WindDir", "time_of_meas_shift": None, "unit": "deg"},
    # "wind_gust_max_last_12h": None,
    # "wind_gust_max_last_1h": None,
    # "wind_gust_max_last_3h": None,
    "wind_speed": {"core_name": "WindSpeed", "time_of_meas_shift": None, "unit": "m/s"}
}


def DWD_historical_to_core_data(
    df_import: pd.DataFrame, start: datetime, stop: datetime, meta: MetaData
) -> pd.DataFrame:
    """
    Transform imported weather data from DWD historical format into core data format.

    Args:
        df_import (pd.DataFrame): The DataFrame containing imported weather data from DWD.
        start (datetime): The timestamp for the start of the desired data range (will be extended for interpolation).
        stop (datetime): The timestamp for the end of the desired data range (will be extended for interpolation).
        meta (MetaData): Metadata associated with the data.

    Returns:
        pd.DataFrame: The transformed DataFrame in the core data format.
    """

    ### evaluate correctness of format
    auxiliary.evaluate_transformations(
        core_format=definitions.format_core_data, other_format=format_DWD_historical
    )

    ### format raw data for further operations
    df = df_import.copy()
    # to datetime; account for different time-formats
    date_format = "%Y%m%d%H%M"
    df.index = pd.to_datetime(df.index, format=date_format)
    # sort by time
    df = df.sort_index()

    # reduce time period to extended period for working interpolation and for faster operation
    df = time_observation_transformations.truncate_data_from_start_to_stop(
        df, start - timedelta(days=1), stop + timedelta(days=1)
    )

    # select only numeric columns
    df = df.select_dtypes(include=["number"])

    # delete dummy values from DWD
    df = auxiliary.replace_dummy_with_nan(df, format_DWD_historical)

    # resample some via sum some via mean -> results in average of following hour
    for var in df.columns:
        if var in variables_to_sum_DWD_historical:
            df[var] = df[var].resample("h").sum(min_count=1)  # fills nan only if 1 value in interval
        else:
            df[var] = df[var].resample("h").mean()  # fills nan only if all nan in interval
    df = df.resample("h").first()  # only keep the previously resampled value

    # rename available variables to core data format
    df = auxiliary.rename_columns(df, format_DWD_historical)

    ### convert timezone to UTC
    # the data is for most stations and datasets, as well as for more recent
    # data (several years) in UTC. For more sophisticated handling pull meta
    # and respect time zone or implement dwd_pulling repo from github

    ### shift and interpolate data forward 30mins or backward -30mins
    df_no_shift = df.copy()
    df = time_observation_transformations.shift_time_by_dict(format_DWD_historical, df)

    def transform_DWD_historical(df):
        # drop unnecessary variables
        df = auxiliary.force_data_variable_convention(df, definitions.format_core_data)

        ### convert units
        df["AtmPressure"] = unit_conversions.hPa_to_Pa(df["AtmPressure"])
        df["DiffHorRad"] = unit_conversions.Jcm2_to_Whm2(df["DiffHorRad"])
        df["GlobHorRad"] = unit_conversions.Jcm2_to_Whm2(df["GlobHorRad"])
        df["HorInfra"] = unit_conversions.Jcm2_to_Whm2(df["HorInfra"])
        df["TotalSkyCover"] = unit_conversions.eigth_to_tenth(df["TotalSkyCover"])

        ### impute missing variables from other available ones
        df, calc_overview = variable_transformations.variable_transform_all(df, meta)

        return df, calc_overview

    df, meta.executed_transformations = transform_DWD_historical(df)

    ### add unshifted data for possible later direct use (pass-through),
    ### to avoid back and forth interpolating
    df = pass_through_handling.create_pass_through_variables(
        df_shifted=df,
        df_no_shift=df_no_shift,
        format=format_DWD_historical,
        transform_func=transform_DWD_historical,
        meta=meta,
    )

    return df


def DWD_forecast_2_core_data(df_import: pd.DataFrame, meta: MetaData) -> pd.DataFrame:
    """
    Transform imported weather forecast data from DWD into core data format.

    Args:
        df_import (pd.DataFrame): The DataFrame containing imported weather forecast data from DWD.
        meta (MetaData): Metadata associated with the data.

    Returns:
        pd.DataFrame: The transformed DataFrame in the core data format.
    """

    ### evaluate correctness of format
    auxiliary.evaluate_transformations(
        core_format=definitions.format_core_data, other_format=format_DWD_forecast
    )

    ### format raw data for further operations
    df = df_import.copy()
    # Resample the DataFrame to make the DatetimeIndex complete and monotonic
    df = df.resample('h').asfreq()
    # delete timezone information
    df = df.tz_localize(None)
    # rename available variables to core data format
    df = auxiliary.rename_columns(df, format_DWD_forecast)

    ### convert timezone to UTC
    # the data pulled by Wetterdienst is already UTC

    ### shift and interpolate data forward 30mins or backward -30mins
    df_no_shift = df.copy()
    df = time_observation_transformations.shift_time_by_dict(format_DWD_forecast, df)

    def transform_DWD_forecast(df):
        # drop unnecessary variables
        df = auxiliary.force_data_variable_convention(df, definitions.format_core_data)

        ### convert units
        df["OpaqueSkyCover"] = unit_conversions.percent_to_tenth(df["OpaqueSkyCover"])
        df["TotalSkyCover"] = unit_conversions.percent_to_tenth(df["TotalSkyCover"])
        df["GlobHorRad"] = unit_conversions.kJm2_to_Whm2(df["GlobHorRad"])
        df["DryBulbTemp"] = unit_conversions.kelvin_to_celcius(df["DryBulbTemp"])
        df["DewPointTemp"] = unit_conversions.kelvin_to_celcius(df["DewPointTemp"])
        df["Visibility"] = unit_conversions.divide_by_1000(df["Visibility"])

        ### impute missing variables from other available ones
        df, calc_overview = variable_transformations.variable_transform_all(df, meta)

        return df, calc_overview

    df, meta.executed_transformations = transform_DWD_forecast(df)

    ### add unshifted data for possible later direct use (pass-through),
    ### to avoid back and forth interpolating
    df = pass_through_handling.create_pass_through_variables(
        df_shifted=df,
        df_no_shift=df_no_shift,
        format=format_DWD_forecast,
        transform_func=transform_DWD_forecast,
        meta=meta,
    )

    return df
