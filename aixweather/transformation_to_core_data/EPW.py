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

logger = logging.getLogger(__name__)


class EPWFormat:
    """
    Information on EPW format:
    Online sources for EPW data: https://climate.onebuilding.org/default.html and
    https://www.ladybug.tools/epwmap/

    Format info:
        - key = output data point name
        - core_name = corresponding name matching the format_core_data
        - time_of_meas_shift = desired 30min shifting+interpolation to convert the value that is "at
          indicated time" to "average of preceding hour" (ind2prec).
        - unit = unit of the output data following the naming convention of format_core_data
        - nan = The default values stated from the format information, those values are
          filled if nan.

    All changes here automatically change the calculations.
    Exception: unit conversions have to be added manually.

    Information for shifting:
        Hour: This is the hour of the data. (1 - 24). Hour 1 is 00:01 to 01:00.
        Cannot be missing. but e.g.:
        DryBulbTemp: This is the dry bulb temperature in C at the time indicated. and:
        GlobHorRad: received on a horizontal surface during the hour preceding the time indicated.
        ----> Hence, we assume that hour 1 should show the DryBulbTemp from
        0:30 to 1:30, i.e. the Temp at indicated time.

    time of measurement checked by Martin Rätz (07.08.2023)
    units checked by Martin Rätz (07.08.2023)
    """

    @classmethod
    def import_format(cls) -> dict:
        """
        Inverts the export format from core2export to import2core
        """
        export_format = cls.export_format()
        import_format = deepcopy(export_format)
        for key, value in import_format.items():
            time_shift = value["time_of_meas_shift"]
            if time_shift == "ind2prec":
                value["time_of_meas_shift"] = "prec2ind"
            elif time_shift == "ind2foll":
                value["time_of_meas_shift"] = "foll2ind"
        return import_format

    @classmethod
    def export_format(cls) -> dict:
        return {
            "Year": {"core_name": "", "unit": "year", "time_of_meas_shift": None, "nan": None},
            "Month": {"core_name": "", "unit": "month", "time_of_meas_shift": None, "nan": None},
            "Day": {"core_name": "", "unit": "day", "time_of_meas_shift": None, "nan": None},
            "Hour": {"core_name": "", "unit": "hour", "time_of_meas_shift": None, "nan": None},
            "Minute": {"core_name": "", "unit": "minute", "time_of_meas_shift": None, "nan": None},
            "Data Source and Uncertainty Flags": {"core_name": "", "unit": None, "time_of_meas_shift": None, "nan": "?"},
            "DryBulbTemp": {"core_name": "DryBulbTemp", "unit": "degC", "time_of_meas_shift": None, "nan": 99.9},
            "DewPointTemp": {"core_name": "DewPointTemp", "unit": "degC", "time_of_meas_shift": None, "nan": 99.9},
            "RelHum": {"core_name": "RelHum", "unit": "percent", "time_of_meas_shift": None, "nan": 999.0},
            "AtmPressure": {"core_name": "AtmPressure", "unit": "Pa", "time_of_meas_shift": None, "nan": 999999.0},
            "ExtHorRad": {"core_name": "ExtHorRad", "unit": "Wh/m2", "time_of_meas_shift": 'ind2prec', "nan": 9999.0},
            "ExtDirNormRad": {"core_name": "ExtDirNormRad", "unit": "Wh/m2", "time_of_meas_shift": 'ind2prec', "nan": 9999.0},
            "HorInfra": {"core_name": "HorInfra", "unit": "Wh/m2", "time_of_meas_shift": 'ind2prec', "nan": 9999.0},
            "GlobHorRad": {"core_name": "GlobHorRad", "unit": "Wh/m2", "time_of_meas_shift": 'ind2prec', "nan": 9999.0},
            "DirNormRad": {"core_name": "DirNormRad", "unit": "Wh/m2", "time_of_meas_shift": 'ind2prec', "nan": 9999.0},
            "DiffHorRad": {"core_name": "DiffHorRad", "unit": "Wh/m2", "time_of_meas_shift": 'ind2prec', "nan": 9999.0},
            "GlobHorIll": {"core_name": "GlobHorIll", "unit": "lux", "time_of_meas_shift": 'ind2prec', "nan": 999999.0},
            "DirecNormIll": {"core_name": "DirecNormIll", "unit": "lux", "time_of_meas_shift": 'ind2prec', "nan": 999999.0},
            "DiffuseHorIll": {"core_name": "DiffuseHorIll", "unit": "lux", "time_of_meas_shift": 'ind2prec', "nan": 999999.0},
            "ZenithLum": {"core_name": "ZenithLum", "unit": "Cd/m2", "time_of_meas_shift": 'ind2prec', "nan": 9999.0},
            "WindDir": {"core_name": "WindDir", "unit": "deg", "time_of_meas_shift": None, "nan": 999.0},
            "WindSpeed": {"core_name": "WindSpeed", "unit": "m/s", "time_of_meas_shift": None, "nan": 999.0},
            "TotalSkyCover": {"core_name": "TotalSkyCover", "unit": "1tenth", "time_of_meas_shift": None, "nan": 99},
            "OpaqueSkyCover": {"core_name": "OpaqueSkyCover", "unit": "1tenth", "time_of_meas_shift": None, "nan": 99},
            "Visibility": {"core_name": "Visibility", "unit": "km", "time_of_meas_shift": None, "nan": 9999.0},
            "CeilingH": {"core_name": "CeilingH", "unit": "m", "time_of_meas_shift": None, "nan": 99999},
            "WeatherObs": {"core_name": "", "unit": "None", "time_of_meas_shift": None, "nan": 9},
            "WeatherCode": {"core_name": "", "unit": "None", "time_of_meas_shift": None, "nan": 999999999},
            "PrecWater": {"core_name": "PrecWater", "unit": "mm", "time_of_meas_shift": None, "nan": 999.0},
            "Aerosol": {"core_name": "Aerosol", "unit": "1thousandth", "time_of_meas_shift": None, "nan": 0.999},
            "Snow": {"core_name": "", "unit": "cm", "time_of_meas_shift": None, "nan": 999.0},
            "DaysSinceSnow": {"core_name": "", "unit": "days", "time_of_meas_shift": None, "nan": 99},
            "Albedo": {"core_name": "", "unit": "None", "time_of_meas_shift": None, "nan": 999},
            "LiquidPrecD": {"core_name": "LiquidPrecD", "unit": "mm/h", "time_of_meas_shift": None, "nan": 999},
            "LiquidPrepQuant": {"core_name": "", "unit": "hours", "time_of_meas_shift": None, "nan": 99},
        }


def EPW_to_core_data(df_import: pd.DataFrame, meta: MetaData) -> pd.DataFrame:
    """
    Transform imported EPW (EnergyPlus Weather) data into core data format.

    Args:
        df_import (pd.DataFrame): The DataFrame containing imported EPW weather data.
        meta (MetaData): Metadata associated with the data.

    Returns:
        pd.DataFrame: The transformed DataFrame in the core data format.
    """
    format_epw = EPWFormat.import_format()

    # evaluate correctness of format
    auxiliary.evaluate_transformations(
        core_format=definitions.format_core_data, other_format=format_epw
    )

    def epw_to_datetimeindex(df):
        '''
        Convert the first 4 columns of the DataFrame to a DatetimeIndex and set it as the
        index.'''
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
    df = df.resample("h").asfreq()
    # give names to columns according to documentation of import data
    df.columns = [key for key in format_epw.keys()]
    # rename available variables to core data format
    df = auxiliary.rename_columns(df, format_epw)
    # delete dummy values from EPW
    df = auxiliary.replace_dummy_with_nan(df, format_epw)

    ### convert timezone to UTC+0
    df = df.shift(periods=-meta.timezone, freq="h", axis=0)

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
