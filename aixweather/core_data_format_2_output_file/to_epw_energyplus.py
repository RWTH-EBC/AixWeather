"""
convert core data to epw (EnergyPlus) data
"""

import csv
import datetime as dt
import pandas as pd
import numpy as np

from aixweather import definitions
from aixweather.imports.utils_import import MetaData
from aixweather.transformation_functions import auxiliary, time_observation_transformations, pass_through_handling

"""
format_epw information:
for links see readme

Information for shifting:
Hour: This is the hour of the data. (1 - 24). Hour 1 is 00:01 to 01:00. Cannot be missing.
but e.g.:
DryBulbTemp: This is the dry bulb temperature in C at the time indicated.
and:
GlobHorRad: received on a horizontal surface during the hour preceding the time indicated.
----> Hence, we assume that hour 1 should show the DryBulbTemp from
0:30 to 1:30, i.e. the Temp at indicated time.

time of measurement checked by Martin Rätz (07.08.2023)
units checked by Martin Rätz (07.08.2023)
"""
format_epw = {
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


def to_epw(
    core_df: pd.DataFrame,
    meta: MetaData,
    start: dt.datetime,
    stop: dt.datetime,
    fillna: bool,
    result_folder: str = None
) -> pd.DataFrame:
    """Create an EPW file from the core data.

    Args:
        core_df (pd.DataFrame): DataFrame containing core data.
        meta (MetaData): Metadata associated with the weather data.
        start (dt.datetime): Timestamp for the start of the EPW file.
        stop (dt.datetime): Timestamp for the end of the EPW file.
        fillna (bool): Boolean indicating whether NaN values should be filled.

    Returns:
        pd.DataFrame: DataFrame containing the weather data formatted for EPW export,
                      excluding metadata.
    """

    ### evaluate correctness of format
    auxiliary.evaluate_transformations(
        core_format=definitions.format_core_data, other_format=format_epw
    )

    df = core_df.copy()

    filename = (
        f"{meta.station_id}_{start.strftime('%Y%m%d')}_{stop.strftime('%Y%m%d')}"
        f"_{meta.station_name}.epw"
    )
    # get file path to safe data to
    file_path = definitions.results_file_path(filename, result_folder)

    ### create header lines
    def line1_location(
        meta: MetaData,
    ):
        """
        Get location metadata (station name, state, country, data_type,
        stationID, lat, lon, TZ, alt)

        return:
            location:      List        Erstezeile(LOCATION) von epw Daten als List
        """

        data_type = ""
        timezone = 0  # relative to UTC

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

    def line2_design_cond():
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

    def line3_typ_ext_period(df):
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
            """Gruppefunktion für df.groupby()"""
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

    def line4_ground_temp(df):
        """
        Parsen von weatherdata, um Bodentemperaturen zu holen

        return:
            ground_temp:    List    Vierte Zeile(GROUND TEMPERATURES) von epw Daten als List
        """

        ground_temp = [
            "GROUND TEMPERATURES",
        ]

        df_w_ground = (
            df.resample("M").mean().copy().round(decimals=1)
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
            print(
                f"For adding the probably unnecessary ground temperature to the .epw file header, "
                f"the following made it impossible: {err}"
            )
            ground_temp = ground_temp + [0]  # 0 ground layers

            return ground_temp

    def line5_holiday_dl_saving(df):
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

    def line6_comment_1():
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

    def line7_comment_2(comment2=None):
        """
        Erstellen der 7. Zeile der epw.

        return:
            comment_2:    List    7.Zeile(COMMENTS 2) von epw Daten als List
        """
        return ["COMMENTS 2", comment2]

    def line8_data_periods(df):
        """
        Parsen von weatherdata, um Start- und Enddatenpunkt zu holen

        return:
            data_periods:    List    8.Zeile(DATA PERIODS) von epw Daten als List
        """
        start_dp = df.index[0]
        end_dp = df.index[-2]
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

    ### parse actual data
    def format_data(df, start, stop):
        """
        Parsen von weatherdata, für den export

        return:
            data_list:    List    Datasätze von epw Daten als List
        """

        # add 1 hour to start, because epw always starts at hour 1 instead of 0
        start_epw = start + dt.timedelta(hours=1)

        ### measurement time conversion
        df = time_observation_transformations.shift_time_by_dict(format_epw, df)

        ### if possible avoid back and forth interpolating -> pass through
        ### variables without shifting
        df = pass_through_handling.pass_through_measurements_with_back_and_forth_interpolating(
           df, format_epw
        )

        ### select only desired period
        df = time_observation_transformations.truncate_data_from_start_to_stop(
            df, start_epw, stop
        )

        ### select the desired columns
        df = auxiliary.force_data_variable_convention(df, format_epw)

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
            df = auxiliary.fill_nan_from_format_dict(df, format_epw)

        # cut off float digits (required for EnergyPlus)
        df = df.applymap(lambda x: (f"{x:.1f}") if isinstance(x, float) else x)

        # again make sure correct order and variables are applied
        # (processing might have mixed it up)
        df = auxiliary.force_data_variable_convention(df, format_epw)

        ### format dataframe to list
        data_list = df[format_epw.keys()].to_numpy().tolist()

        return data_list, df

    ### merge all header lines and the data to be saved in a .epw file
    with open(file_path, "w", newline="", encoding="latin1") as file:
        writer = csv.writer(file)
        writer.writerows(
            [
                line1_location(meta),
                line2_design_cond(),
                line3_typ_ext_period(df),
                line4_ground_temp(df),
                line5_holiday_dl_saving(df),
                line6_comment_1(),
                line7_comment_2(),
                line8_data_periods(df),
            ]
        )
        df_as_list, df = format_data(df, start, stop)
        writer.writerows(df_as_list)

    print(f"EPW file saved to {file_path}.")

    return df
