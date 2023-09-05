"""
Converts core data to modelica TMY3Reader data
"""

import calendar
import datetime as dt
import pandas as pd

from AixWeather.imports.utils_import import MetaData
from AixWeather.core_data_format_2_output_file import utils_2output
from AixWeather.transformation_functions import auxiliary, time_observation_transformations, pass_through_handling

"""
format_modelica_TMY3 information:

Please indicate the unit (conversion has to be changed manually)
Please indicate the desired time of measurement (conversion automatically)
The stated nans are the default values stated from the AixLib TMY3 Reader, those values are filled if nan.

time_of_meas_shift´s checked by Martin Rätz (07.08.2023)
unit´s checked by Martin Rätz (07.08.2023)
"""
format_modelica_TMY3 = {
    'timeOfYear': {'core_name': '', 'unit': 's', 'time_of_meas_shift': None, 'nan': None},
    'DryBulbTemp': {'core_name': 'DryBulbTemp', 'unit': 'degC', 'time_of_meas_shift': None, 'nan': 20.0},
    'DewPointTemp': {'core_name': 'DewPointTemp', 'unit': 'degC', 'time_of_meas_shift': None, 'nan': 10.0},
    'RelHum': {'core_name': 'RelHum', 'unit': 'percent', 'time_of_meas_shift': None, 'nan': 50},
    'AtmPressure': {'core_name': 'AtmPressure', 'unit': 'Pa', 'time_of_meas_shift': None, 'nan': 101325},
    'ExtHorRad': {'core_name': 'ExtHorRad', 'unit': 'Wh/m2', 'time_of_meas_shift': 'ind2prec', 'nan': '-0'},
    'ExtDirNormRad': {'core_name': 'ExtDirNormRad', 'unit': 'Wh/m2', 'time_of_meas_shift': 'ind2prec', 'nan': '-0'},
    'HorInfra': {'core_name': 'HorInfra', 'unit': 'Wh/m2', 'time_of_meas_shift': 'ind2prec', 'nan': 0},
    'GlobHorRad': {'core_name': 'GlobHorRad', 'unit': 'Wh/m2', 'time_of_meas_shift': 'ind2prec', 'nan': 0},
    'DirNormRad': {'core_name': 'DirNormRad', 'unit': 'Wh/m2', 'time_of_meas_shift': 'ind2prec', 'nan': 0},
    'DiffHorRad': {'core_name': 'DiffHorRad', 'unit': 'Wh/m2', 'time_of_meas_shift': 'ind2prec', 'nan': 0},
    'GlobHorIll': {'core_name': 'GlobHorIll', 'unit': 'lux', 'time_of_meas_shift': 'ind2prec', 'nan': '-0'},
    'DirecNormIll': {'core_name': 'DirecNormIll', 'unit': 'lux', 'time_of_meas_shift': 'ind2prec', 'nan': '-0'},
    'DiffuseHorIll': {'core_name': 'DiffuseHorIll', 'unit': 'lux', 'time_of_meas_shift': 'ind2prec', 'nan': '-0'},
    'ZenithLum': {'core_name': 'ZenithLum', 'unit': 'Cd/m2', 'time_of_meas_shift': 'ind2prec', 'nan': '-0'},
    'WindDir': {'core_name': 'WindDir', 'unit': 'deg', 'time_of_meas_shift': None, 'nan': '-0'},
    'WindSpeed': {'core_name': 'WindSpeed', 'unit': 'm/s', 'time_of_meas_shift': None, 'nan': '-0'},
    'TotalSkyCover': {'core_name': 'TotalSkyCover', 'unit': '1tenth', 'time_of_meas_shift': None, 'nan': 5},
    'OpaqueSkyCover': {'core_name': 'OpaqueSkyCover', 'unit': '1tenth', 'time_of_meas_shift': None, 'nan': 5},
    'Visibility': {'core_name': 'Visibility', 'unit': 'km', 'time_of_meas_shift': None, 'nan': '-0'},
    'CeilingH': {'core_name': 'CeilingH', 'unit': 'm', 'time_of_meas_shift': None, 'nan': 20000.0},
    'WeatherObs': {'core_name': '', 'unit': '', 'time_of_meas_shift': None, 'nan': '-0'},
    'WeatherCode': {'core_name': '', 'unit': '', 'time_of_meas_shift': None, 'nan': '-0'},
    'PrecWater': {'core_name': 'PrecWater', 'unit': 'mm', 'time_of_meas_shift': None, 'nan': '-0'},
    'Aerosol': {'core_name': 'Aerosol', 'unit': '1thousandth', 'time_of_meas_shift': None, 'nan': '-0'},
    'Snow': {'core_name': '', 'unit': 'cm', 'time_of_meas_shift': None, 'nan': '-0'},
    'DaysSinceSnow': {'core_name': '', 'unit': 'days', 'time_of_meas_shift': None, 'nan': '-0'},
    'Albedo': {'core_name': '', 'unit': '', 'time_of_meas_shift': None, 'nan': '-0'},
    'LiquidPrecD': {'core_name': 'LiquidPrecD', 'unit': 'mm/h', 'time_of_meas_shift': None, 'nan': '-0'},
    'LiquidPrepQuant': {'core_name': '', 'unit': '', 'time_of_meas_shift': None, 'nan': '-0'}
}


def to_mos(
    core_df: pd.DataFrame,
    meta: MetaData,
    start: dt.datetime,
    stop: dt.datetime,
    fillna: bool
) -> pd.DataFrame:
    """Create a MOS file from the core data.

    Args:
        core_df (pd.DataFrame): DataFrame containing core data.
        meta (MetaData): Metadata associated with the weather data.
        start (dt.datetime): Timestamp for the start of the MOS file.
        stop (dt.datetime): Timestamp for the end of the MOS file.
        fillna (bool): Boolean indicating whether NaN values should be filled.

    Returns:
        pd.DataFrame: DataFrame containing the weather data formatted for MOS export,
                      excluding metadata.
    """
    ### evaluate correctness of format
    auxiliary.evaluate_transformations(
        core_format=auxiliary.format_core_data, other_format=format_modelica_TMY3
    )

    df = core_df.copy()

    ### measurement time conversion
    df = time_observation_transformations.shift_time_by_dict(format_modelica_TMY3, df)

    ### if possible avoid back and forth interpolating -> pass through variables without shifting
    df = pass_through_handling.pass_through_measurements_with_back_and_forth_interpolating(
        df, format_modelica_TMY3
    )

    ### select only desired period
    df = time_observation_transformations.truncate_data_from_start_to_stop(
        df, start, stop
    )

    ### select the desired columns
    df = auxiliary.force_data_variable_convention(df, format_modelica_TMY3)

    # tmy3 data must start with 0 at the beginning of year (due to internal
    # tmy3_reader sun inclination calculation)
    min_year = min(df.index.year)
    time_of_year = (
            (df.index.year - min_year) * 365 * 24 * 3600
            + calendar.leapdays(min_year, df.index.year) * 24 * 3600
            + (df.index.dayofyear - 1) * 24 * 3600
            + df.index.hour * 3600
    )
    df["timeOfYear"] = time_of_year

    # to avoid having the one-year duration between start and end of data as
    # it will make the tmy3_reader loop the data
    if (df["timeOfYear"].iloc[-1] - df["timeOfYear"].iloc[0]) == 365 * 24 * 3600:
        # copy last row
        last_row = df.iloc[-1]

        # Convert the Series to a new DataFrame with a single row
        new_row_df = last_row.to_frame().T

        # continue time values
        new_row_df["timeOfYear"].iloc[0] = new_row_df["timeOfYear"].iloc[0] + 3600
        new_row_df.index = new_row_df.index + dt.timedelta(hours=1)

        # add new row to df, make sure its int
        df = pd.concat([df, new_row_df])
        df["timeOfYear"] = df["timeOfYear"].astype(int)

    ### fill nan
    if fillna:
        # fill first and last lines nans (possibly lost through shifting)
        df.iloc[0, :] = df.bfill().iloc[0, :]
        df.iloc[-1, :] = df.ffill().iloc[-1, :]
        # fill dummy values
        auxiliary.fill_nan_from_format_dict(df, format_modelica_TMY3)

    ### Create header
    header_of = (
        "#1:for TMY3reader"
        + "\ndouble tab1("
        + str(int(df.index.size))
        + ","
        + str(int(df.columns.size))
        + ")"
    )
    header_of += f"\n#LOCATION,{meta.station_name},,,,,{str(meta.latitude)}," \
                 f"{str(meta.longitude)},0,something"
    header_of += (
        "\n#Explanation of Location line:"
        + "\n#   Element 7: latitude"
        + "\n#   Element 8: longitude"
        + "\n#   Element 9: time zone in hours from UTC"
        + "\n#"
    )

    # Data periods
    header_of += (
        "\n#DATA PERIODS, data available from "
        + str(dt.datetime.strptime(str(df.index[0]), "%Y-%m-%d %H:%M:%S"))
        + " "
        + "(second="
        + str(df["timeOfYear"].iloc[0])
        + ") to "
        + str(dt.datetime.strptime(str(df.index[-1]), "%Y-%m-%d %H:%M:%S"))
        + " "
        + "(second="
        + str(df["timeOfYear"].iloc[-1])
        + ")"
        + "\n# info: TMY3Reader requirement: Time 0 = 01.01. 00:00:00 at local"
          " time (see time zone above)"
        + "\n#"
    )
    # data source
    header_of += (
        "\n#USED DATA-COLLECTOR: "
        + "ebc-weather-tool with input source "
        + str(meta.input_source)
        + " (collected at "
        + str(dt.datetime.now())
        + ') "-0" marks not available data'
        "\n#Info: The AixLib/IBPSA TMY3reader requires the below mentioned units and"
          " measurement times. Last Check: 28.02.2022"
    )

    # Information about the data
    header_of += (
        "\n#C1 Time in seconds. Beginning of a year is 0s."
        + "\n#C2 Dry bulb temperature in Celsius at indicated time"
        + "\n#C3 Dew point temperature in Celsius at indicated time"
        + "\n#C4 Relative humidity in percent at indicated time"
        + "\n#C5 Atmospheric station pressure in Pa at indicated time, TMY3Reader:"
          " not used per default"
        + "\n#C6 Extraterrestrial horizontal radiation in Wh/m2, TMY3Reader: not used"
        + "\n#C7 Extraterrestrial direct normal radiation in Wh/m2, TMY3Reader: not used"
        + "\n#C8 Horizontal infrared radiation intensity in Wh/m2"
        + "\n#C9 Global horizontal radiation in Wh/m2"
        + "\n#C10 Direct normal radiation in Wh/m2"
        + "\n#C11 Diffuse horizontal radiation in Wh/m2"
        + "\n#C12 Averaged global horizontal illuminance in lux during minutes preceding"
          " the indicated time, TMY3Reader: not used"
        + "\n#C13 Direct normal illuminance in lux during minutes preceding the"
          " indicated time, TMY3Reader: not used"
        + "\n#C14 Diffuse horizontal illuminance in lux during minutes preceding the"
          " indicated time, TMY3Reader: not used"
        + "\n#C15 Zenith luminance in Cd/m2 during minutes preceding the indicated"
          " time, TMY3Reader: not used"
        + "\n#C16 Wind direction at indicated time. N=0, E=90, S=180, W=270"
        + "\n#C17 Wind speed in m/s at indicated time"
        + "\n#C18 Total sky cover in tenth at indicated time"
        + "\n#C19 Opaque sky cover tenth indicated time"
        + "\n#C20 Visibility in km at indicated time, TMY3Reader: not used"
        + "\n#C21 Ceiling height in m"
        + "\n#C22 Present weather observation, TMY3Reader: not used"
        + "\n#C23 Present weather codes, TMY3Reader: not used"
        + "\n#C24 Precipitable water in mm, TMY3Reader: not used"
        + "\n#C25 Aerosol optical depth, TMY3Reader: not used"
        + "\n#C26 Snow depth in cm, TMY3Reader: not used"
        + "\n#C27 Days since last snowfall, TMY3Reader: not used"
        + "\n#C28 Albedo, TMY3Reader: not used"
        + "\n#C29 Liquid precipitation depth in mm/h at indicated time, TMY3Reader: not used"
        + "\n#C30 Liquid precipitation quantity, TMY3Reader: not used"
    )

    ### write to csv
    filename = (
        f"{meta.station_id}_{start.strftime('%Y%m%d')}_{stop.strftime('%Y%m%d')}"
        f"_{meta.station_name}.mos"
    )
    filepath = utils_2output.results_file_path(filename)

    df.to_csv(
        filepath,
        sep="\t",
        float_format="%.2f",
        header=False,
        index_label="timeOfYear",
        index=False,
    )

    # Read the contents and prepend the header_of to the file
    with open(filepath, "r+") as file:
        content = file.read()
        file.seek(0, 0)
        file.write(f"{header_of}\n{content}")

    print(f"MOS file saved to {filepath}.")
    return df
