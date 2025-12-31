"""
convert core data to epw (EnergyPlus) data
"""

import csv
import datetime as dt
import logging

import pandas as pd
import numpy as np

from aixweather import definitions
from aixweather.imports.utils_import import MetaData
from aixweather.transformation_functions import auxiliary, time_observation_transformations, pass_through_handling
from aixweather.transformation_to_core_data.EPW import EPWFormat

logger = logging.getLogger(__name__)


def to_epw(
        core_df: pd.DataFrame,
        meta: MetaData,
        start: dt.datetime,
        stop: dt.datetime,
        fillna: bool,
        result_folder: str = None,
        filename: str = None,
        export_in_utc: bool = False
) -> (pd.DataFrame, str):
    """Create an EPW file from the core data.

    Args:
        core_df (pd.DataFrame): DataFrame containing core data.
        meta (MetaData): Metadata associated with the weather data.
        start (dt.datetime): Timestamp for the start of the EPW file.
        stop (dt.datetime): Timestamp for the end of the EPW file.
        fillna (bool): Boolean indicating whether NaN values should be filled.
        result_folder (str):
            Path to the folder where to save the file. Default will use
            the `results_file_path` method.
        filename (str): Name of the file to be saved. The default is constructed
            based on the meta-data as well as start and stop time
        export_in_utc (bool): Timezone to be used for the export.
            True (default) to use the core_df timezone, UTC+0,
            False (default) to use timezone from metadata

    Returns:
        pd.DataFrame: DataFrame containing the weather data formatted for EPW export,
                      excluding metadata.
        str: Path to the exported file.
    """
    timezone = 0 if export_in_utc else meta.timezone

    ### evaluate correctness of format
    auxiliary.evaluate_transformations(
        core_format=definitions.format_core_data, other_format=EPWFormat.export_format()
    )

    df = core_df.copy()

    # format data to epw
    df_epw_as_list, df_epw = _format_data(
        df=df, start=start, stop=stop, timezone=timezone, fillna=fillna
    )

    # get final start and stop time (differs from start, stop due to filling to full days)
    start_epw = pd.to_datetime(df_epw.iloc[[0]][['Year', 'Month', 'Day', 'Hour']]).iloc[0]
    stop_epw = pd.to_datetime(df_epw.iloc[[-1]][['Year', 'Month', 'Day', 'Hour']]).iloc[-1]
    # truncate core data for other calculations
    df_truncated = time_observation_transformations.truncate_data_from_start_to_stop(
        df, start_epw, stop_epw
    )

    # keep regular start stop in the filename for the unit tests
    if filename is None:
        _utc_flag = "_utc" if export_in_utc else ""
        filename = (
            f"{meta.station_id}_{start.strftime('%Y%m%d')}_{stop.strftime('%Y%m%d')}"
            f"_{meta.station_name}{_utc_flag}.epw"
        )
    # get file path to safe data to
    file_path = definitions.results_file_path(filename, result_folder)

    ### merge all header lines and the data to be saved in a .epw file
    with open(file_path, "w", newline="", encoding="latin1") as file:
        writer = csv.writer(file)
        writer.writerows(
            [
                _line1_location(meta=meta, timezone=timezone),
                _line2_design_cond(),
                _line3_typ_ext_period(df_truncated),
                _line4_ground_temp(df_truncated),
                _line5_holiday_dl_saving(df_truncated),
                _line6_comment_1(),
                _line7_comment_2(),
                _line8_data_periods(df_truncated),
            ]
        )
        writer.writerows(df_epw_as_list)

    logger.info("EPW file saved to %s.", file_path)

    return df, file_path


### create header lines
def _line1_location(
        meta: MetaData,
        timezone: int
):
    """
    Get location metadata (station name, state, country, data_type,
    stationID, lat, lon, TZ, alt)

    return:
        location:      List        Erstezeile(LOCATION) von epw Daten als List
    """

    data_type = ""

    location = [
        "LOCATION",
        meta.station_name,
        "State",
        "country",
        data_type,
        meta.station_id,
        str(meta.latitude),
        str(meta.longitude),
        timezone,
        str(meta.altitude),
    ]

    return location


def _line2_design_cond():
    """
    Erstellen zweite Zeile der epw.

    return:
        design_cond:    List    Zweite Zeile(Design Condition) von epw Daten als List
    """
    design_cond = [
        "DESIGN CONDITIONS",
        0,  # number of design condition
    ]

    return design_cond


def _line3_typ_ext_period(df):
    """
    Parsen von weatherdata um typische und extreme Perioden zu holen.

    Typische Perioden sind Wochen mit Temperatur, die der Durchschnittstemperatur der Saison
    am nächsten kommt.
    Extreme Perioden sind Wochen mit Temperatur, die der Maximum-/Minimumtemperatur der Saison
    am nächsten kommt.

    return:
        typical_extreme_period:     List    Dritte Zeile(TYPICAL/EXTREME PERIODS)
                                                von epw Daten als List
    """

    typical_extreme_period = [
        "TYPICAL/EXTREME PERIODS",
    ]

    season_dict = {
        11: "Autumn",
        12: "Winter",
        1: "Winter",
        2: "Winter",
        3: "Spring",
        4: "Spring",
        5: "Spring",
        6: "Summer",
        7: "Summer",
        8: "Summer",
        9: "Autumn",
        10: "Autumn",
    }  # Monaten in Saisons zuweisen

    def group_func(input):
        """Gruppefunktion für .groupby()"""
        return season_dict[input.month]

    df_temp_ambient = df["DryBulbTemp"]  # Temperature_Ambient von weatherdata holen
    number_of_periods = (
        df_temp_ambient.groupby(group_func).mean().shape[0]
    )  # Zahl von der Saisons rechnen als Zahl von Perioden
    typical_extreme_period.append(number_of_periods)

    # Gruppierung per Saison
    try:
        summer_temp = df_temp_ambient.groupby(group_func).get_group("Summer")
    except KeyError:
        summer_temp = pd.DataFrame()
    try:
        spring_temp = df_temp_ambient.groupby(group_func).get_group("Spring")
    except KeyError:
        spring_temp = pd.DataFrame()
    try:
        autumn_temp = df_temp_ambient.groupby(group_func).get_group("Autumn")
    except KeyError:
        autumn_temp = pd.DataFrame()
    try:
        winter_temp = df_temp_ambient.groupby(group_func).get_group("Winter")
    except KeyError:
        winter_temp = pd.DataFrame()

    if not summer_temp.empty:
        typical_extreme_period[1] = (
                typical_extreme_period[1] + 1
        )  # Summer und Winter haben extreme Periode.
        max_temp_summer = summer_temp.max()
        typ_temp_summer = summer_temp.mean()
        summer_temp_w = summer_temp.resample(
            "W", label="left"
        ).mean()  # Resample in wochentliche Interval

        # Datenpunkt(typisch und extreme) finden
        idx_mean_summer = summer_temp_w.sub(typ_temp_summer).abs().idxmin()
        idx_max_summer = summer_temp_w.sub(max_temp_summer).abs().idxmin()
        week_closest2mean_summer = summer_temp_w.loc[[idx_mean_summer]]  # Starttag
        week_closest2max_summer = summer_temp_w.loc[[idx_max_summer]]  # Starttag

        # Endtag berechnen
        weekend_max_summer = week_closest2max_summer.index + dt.timedelta(days=6)
        weekend_mean_summer = week_closest2mean_summer.index + dt.timedelta(days=6)

        # List für die Saison erstellen
        summer = [
            "Summer - Week Nearest Max Temperature For Period",
            "Extreme",
            str(week_closest2max_summer.index.month[0])
            + "/"
            + str(week_closest2max_summer.index.day[0]),
            str(weekend_max_summer.month[0]) + "/" + str(weekend_max_summer.day[0]),
            "Summer - Week Nearest Average Temperature For Period",
            "Typical",
            str(week_closest2mean_summer.index.month[0])
            + "/"
            + str(week_closest2mean_summer.index.day[0]),
            str(weekend_mean_summer.month[0])
            + "/"
            + str(weekend_mean_summer.day[0]),
        ]

        typical_extreme_period = (
                typical_extreme_period + summer
        )  # Liste zusammensetzen

    # für alle Saison wiederholen
    if not winter_temp.empty:
        typical_extreme_period[1] = typical_extreme_period[1] + 1
        min_temp_winter = winter_temp.min()
        typ_temp_winter = winter_temp.mean()
        winter_temp_w = winter_temp.resample("W", label="left").mean()
        idx_mean_winter = winter_temp_w.sub(typ_temp_winter).abs().idxmin()
        idx_min_winter = winter_temp_w.sub(min_temp_winter).abs().idxmin()
        week_closest2mean_winter = winter_temp_w.loc[[idx_mean_winter]]
        week_closest2min_winter = winter_temp_w.loc[[idx_min_winter]]
        weekend_min_winter = week_closest2min_winter.index + dt.timedelta(days=6)
        weekend_mean_winter = week_closest2mean_winter.index + dt.timedelta(days=6)
        winter = [
            "Winter - Week Nearest Min Temperature For Period",
            "Extreme",
            str(week_closest2min_winter.index.month[0])
            + "/"
            + str(week_closest2min_winter.index.day[0]),
            str(weekend_min_winter.month[0]) + "/" + str(weekend_min_winter.day[0]),
            "Winter - Week Nearest Average Temperature For Period",
            "Typical",
            str(week_closest2mean_winter.index.month[0])
            + "/"
            + str(week_closest2mean_winter.index.day[0]),
            str(weekend_mean_winter.month[0])
            + "/"
            + str(weekend_mean_winter.day[0]),
        ]

        typical_extreme_period = typical_extreme_period + winter

    if not autumn_temp.empty:
        typ_temp_autumn = autumn_temp.mean()
        autumn_temp_w = autumn_temp.resample("W", label="left").mean()
        idx_mean_autumn = autumn_temp_w.sub(typ_temp_autumn).abs().idxmin()
        week_closest2mean_autumn = autumn_temp_w.loc[[idx_mean_autumn]]
        weekend_mean_autumn = week_closest2mean_autumn.index + dt.timedelta(days=6)
        autumn = [
            "Autumn - Week Nearest Average Temperature For Period",
            "Typical",
            str(week_closest2mean_autumn.index.month[0])
            + "/"
            + str(week_closest2mean_autumn.index.day[0]),
            str(weekend_mean_autumn.month[0])
            + "/"
            + str(weekend_mean_autumn.day[0]),
        ]

        typical_extreme_period = typical_extreme_period + autumn

    if not spring_temp.empty:
        typ_temp_spring = spring_temp.mean()
        spring_temp_w = spring_temp.resample("W", label="left").mean()
        idx_mean_spring = spring_temp_w.sub(typ_temp_spring).abs().idxmin()
        week_closest2mean_spring = spring_temp_w.loc[[idx_mean_spring]]
        weekend_mean_spring = week_closest2mean_spring.index + dt.timedelta(days=6)
        spring = [
            "Spring - Week Nearest Average Temperature For Period",
            "Typical",
            str(week_closest2mean_spring.index.month[0])
            + "/"
            + str(week_closest2mean_spring.index.day[0]),
            str(weekend_mean_spring.month[0])
            + "/"
            + str(weekend_mean_spring.day[0]),
        ]

        typical_extreme_period = typical_extreme_period + spring

    return typical_extreme_period


def _line4_ground_temp(df):
    """
    Parsen von weatherdata, um Bodentemperaturen zu holen.

    #Todo: Not checked yet if this is calculation is correct

    return:
        ground_temp:    List    Vierte Zeile(GROUND TEMPERATURES) von epw Daten als List
    """

    ground_temp = [
        "GROUND TEMPERATURES",
    ]

    df_4_ground_temp = df.copy()

    df_w_ground = (
        df_4_ground_temp.resample("M").mean().round(decimals=1)
    )  # Resample in monatliche Interval
    try:
        ground_t = df_w_ground[
            [
                "Soil_Temperature_5cm",
                "Soil_Temperature_10cm",
                "Soil_Temperature_20cm",
                "Soil_Temperature_50cm",
                "Soil_Temperature_1m",
            ]
        ].to_numpy()  # Dataframe2Array
        # Array zu Liste umwandeln -> Zusammensetzen
        ground_temp = (
                ground_temp
                + [5]  # ground layers
                + [0.05, None, None, None]
                + ground_t[:, 0].tolist()
                + [0.1, None, None, None]
                + ground_t[:, 1].tolist()
                + [0.2, None, None, None]
                + ground_t[:, 2].tolist()
                + [0.5, None, None, None]
                + ground_t[:, 3].tolist()
                + [1, None, None, None]
                + ground_t[:, 4].tolist()
        )
        return ground_temp
    except KeyError as err:
        logger.warn(
            "Error while adding the probably unnecessary ground temperature to the .epw file "
            "header. A placeholder will be used. Error: %s", err
        )
        ground_temp = ground_temp + [0]  # 0 ground layers

        return ground_temp


def _line5_holiday_dl_saving(df):
    """
    Erstellen der 5. Zeile der epw.

    return:
        holiday_dl_saving:    List    5.Zeile(HOLIDAYS/DAYLIGHT SAVINGS) von epw Daten als List
    """

    if True in df.index.is_leap_year:
        isLeap = "Yes"
    else:
        isLeap = "No"
    holiday_dl_saving = [
        "HOLIDAYS/DAYLIGHT SAVINGS",
        isLeap,  # Leap Year Observed
        0,  # Daylight Saving Start Date
        0,  # Daylight Saving End Date
        0,  # Number of Holidays
    ]
    return holiday_dl_saving


def _line6_comment_1():
    """
    Erstellen der 6. Zeile der epw.

    return:
        comment_1:    List    6.Zeile(COMMENTS 1) von epw Daten als List
    """
    return [
        "COMMENTS 1",
        "For data format information see the code or check: "
        "https://designbuilder.co.uk/cahelp/Content/EnergyPlusWeatherFileFormat.htm",
    ]


def _line7_comment_2(comment2=None):
    """
    Erstellen der 7. Zeile der epw.

    return:
        comment_2:    List    7.Zeile(COMMENTS 2) von epw Daten als List
    """
    return ["COMMENTS 2", comment2]


def _line8_data_periods(df):
    """
    Parsen von weatherdata, um Start- und Enddatenpunkt zu holen

    return:
        data_periods:    List    8.Zeile(DATA PERIODS) von epw Daten als List
    """
    start_dp = df.index[0]
    end_dp = df.index[-1]
    data_periods = [
        "DATA PERIODS",
        1,  # Anzahl von Datenperioden
        1,  # Anzahl von Intervale in einer Stunde
        "Data",  # DP Name oder Beschreibung
        start_dp.strftime("%A"),  # DP Starttag
        start_dp.strftime("%m/%d"),  # DP Startdatum
        end_dp.strftime("%m/%d"),  # DP Enddatum
    ]
    return data_periods

def _format_data(df, start, stop, timezone, fillna):
    """
    Parse actual weatherdata, for export

    return:
        data_list:    List    Datasätze von epw Daten als List
    """
    ### measurement time conversion
    df = time_observation_transformations.shift_time_by_dict(EPWFormat.export_format(), df)

    ### if possible avoid back and forth interpolating -> pass through
    ### variables without shifting
    df = pass_through_handling.pass_through_measurements_with_back_and_forth_interpolating(
        df, EPWFormat.export_format()
    )

    ### select only desired period
    df = time_observation_transformations.truncate_data_from_start_to_stop(
        df, start, stop
    )

    ### Shift to desired timezone
    df = df.shift(periods=timezone, freq="h", axis=0)

    ### select the desired columns
    df = auxiliary.force_data_variable_convention(df, EPWFormat.export_format())

    # fill newly created variables of desired output format
    # Index von Dataframe aufspalten
    df["Year"] = pd.DatetimeIndex(df.index).year
    df["Month"] = pd.DatetimeIndex(df.index).month
    df["Day"] = pd.DatetimeIndex(df.index).day
    df["Hour"] = pd.DatetimeIndex(df.index).hour
    df["Minute"] = pd.DatetimeIndex(df.index).minute

    ### meet special epw requirements
    # Stunden 0 zu 24 der vorherigen Tag umwandeln
    df["Hour"] = df["Hour"].replace([0], 24)
    # Falls Tag ungleich 1 -> Tag substrahieren mit 1
    df.loc[(df["Hour"] == 24) & (df["Day"] != 1), "Day"] = df.loc[
        (df["Hour"] == 24) & (df["Day"] != 1), "Day"
    ].sub(1)
    # Falls Tag gleich 1 -> Jahr, Monat, Tag loeschen -> mit ffill nachfuellen
    df.loc[
        (df["Hour"] == 24) & (df["Day"] == 1),
        ["Year", "Month", "Day"]
    ] = np.nan
    df["Year"] = (
        df["Year"].ffill().bfill().astype(int)
    )
    df["Month"] = (
        df["Month"].ffill().bfill().astype(int)
    )
    df["Day"] = df["Day"].ffill().bfill().astype(int)
    df.reset_index(drop=True, inplace=True)

    # data should always contain full days
    df, first_day_added_rows = fill_full_first_day(df)
    df, last_day_added_rows = fill_full_last_day(df)

    # ensure data type where required
    columns_to_convert = ["Year", "Month", "Day", "Hour", "Minute"]
    for col in columns_to_convert:
        df[col] = df[col].astype(float).astype(int)

    ### fill NaNs
    if fillna:
        # Forward-fill added rows at end of df
        df.iloc[-last_day_added_rows:, :] = df.ffill().iloc[
                                            -last_day_added_rows:, :
                                            ]
        # fill added rows at beginning of df
        df.iloc[:first_day_added_rows, :] = df.bfill().iloc[
                                            :first_day_added_rows, :
                                            ]

        # fill first and last lines nans (possibly lost through shifting)
        df.iloc[0 + first_day_added_rows + 1, :] = df.bfill().iloc[
                                                   0 + first_day_added_rows + 1, :
                                                   ]
        df.iloc[-1 - last_day_added_rows, :] = df.ffill().iloc[
                                               -1 - last_day_added_rows, :
                                               ]

        # fill default nans to the rest
        df = auxiliary.fill_nan_from_format_dict(df, EPWFormat.export_format())

    # cut off float digits (required for EnergyPlus)
    df = df.applymap(lambda x: (f"{x:.1f}") if isinstance(x, float) else x)

    # again make sure correct order and variables are applied
    # (processing might have mixed it up)
    df = auxiliary.force_data_variable_convention(df, EPWFormat.export_format())

    ### format dataframe to list
    data_list = df[EPWFormat.export_format().keys()].to_numpy().tolist()

    return data_list, df


def fill_full_first_day(df):
    # Identify the first hour and date of the DataFrame
    first_minute = df.iloc[0]["Minute"]
    first_hour = df.iloc[0]["Hour"]
    first_day = df.iloc[0]["Day"]
    first_month = df.iloc[0]["Month"]
    first_year = df.iloc[0]["Year"]
    rows_to_add = 0

    # If the first hour is not 1, add rows to start with hour 1
    if first_hour != 1:
        # If the first hour is 24, we dont want to add an full extra day, just delete the
        # line so that the data frame starts with hour 1
        if first_hour == 24:
            df = df.drop(df.index[0])
        else:
            # Calculate how many rows to add
            rows_to_add = int(first_hour) - 1

            # Generate new rows
            for i in range(rows_to_add, 0, -1):
                new_row = pd.DataFrame(
                    {
                        "Minute": [first_minute],
                        "Hour": [i],
                        "Day": [first_day],
                        "Month": [first_month],
                        "Year": [first_year],
                    }
                )
                df = pd.concat([new_row, df]).reset_index(drop=True)
    return df, rows_to_add


def fill_full_last_day(df):
    # Identify the last hour and date of the DataFrame
    last_hour = df.iloc[-1]["Hour"]
    last_day = df.iloc[-1]["Day"]
    last_month = df.iloc[-1]["Month"]
    last_year = df.iloc[-1]["Year"]
    last_minute = df.iloc[-1]["Minute"]
    rows_to_add = 0

    # If the last hour is not 24, add rows to reach hour 24
    if last_hour != 24:
        # If the last hour is 0, we dont want to add a full extra day, just delete the
        # line so that the data frame ends with hour 24
        if last_hour == 0:
            df = df.drop(df.index[-1])
        else:
            # Calculate how many rows to add
            rows_to_add = 24 - int(last_hour)

            # Generate new rows
            new_rows = []
            for i in range(1, rows_to_add + 1):
                new_row = {
                    "Minute": last_minute,
                    "Hour": last_hour + i,
                    "Day": last_day,
                    "Month": last_month,
                    "Year": last_year,
                }
                new_rows.append(new_row)

            # Append new rows to DataFrame
            df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    return df, rows_to_add
