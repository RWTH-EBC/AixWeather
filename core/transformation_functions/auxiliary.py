"""
includes auxiliary functions for data handling and transformation
"""

import pandas as pd
import numpy as np

# core data format always in UTC at indicated time
format_core_data = {
    # from TMY3 https://www.nrel.gov/docs/fy08osti/43156.pdf
    "DryBulbTemp": {"unit": "degC"},
    "DewPointTemp": {"unit": "degC"},
    "RelHum": {"unit": "percent"},
    "ExtHorRad": {"unit": "Wh/m2"},
    "ExtDirNormRad": {"unit": "Wh/m2"},
    "HorInfra": {"unit": "Wh/m2"},
    "GlobHorRad": {"unit": "Wh/m2"},
    "DirNormRad": {"unit": "Wh/m2"},
    "DirHorRad": {"unit": "Wh/m2"},
    "DiffHorRad": {"unit": "Wh/m2"},
    "GlobHorIll": {"unit": "lux"},
    "DirecNormIll": {"unit": "lux"},
    "DiffuseHorIll": {"unit": "lux"},
    "ZenithLum": {"unit": "Cd/m2"},
    "WindDir": {"unit": "deg"},
    "WindSpeed": {"unit": "m/s"},
    "TotalSkyCover": {"unit": "1tenth"},
    "OpaqueSkyCover": {"unit": "1tenth"},
    "Visibility": {"unit": "km"},
    "CeilingH": {"unit": "m"},
    "PrecWater": {"unit": "mm"},
    "Aerosol": {"unit": "1thousandth"},
    "LiquidPrecD": {"unit": "mm/h"},
    # exception to TMY3 format as all TMY3 data file actually use "Pa" instead of mbar
    "AtmPressure": {"unit": "Pa"},
    # additional variables
    "Soil_Temperature_5cm": {"unit": "degC"},
    "Soil_Temperature_10cm": {"unit": "degC"},
    "Soil_Temperature_20cm": {"unit": "degC"},
    "Soil_Temperature_50cm": {"unit": "degC"},
    "Soil_Temperature_1m": {"unit": "degC"},
}


def force_data_variable_convention(df, format_desired):
    """filter data that shall be in desired format and
    make sure all desired variables are present in correct order"""

    # filter existing df
    core_var_names = set(format_desired.keys())
    df_core_var = df.loc[:, df.columns.isin(core_var_names)]

    # Reindex the DataFrame to ensure all required columns exist and obey the order of columns
    df_core_var = df_core_var.reindex(columns=format_desired.keys())

    return df_core_var


def rename_columns(df, format_dict):
    rename_map = {key: val["core_name"] for key, val in format_dict.items()}
    return df.rename(columns=rename_map)


def fill_nan_from_format_dict(df, format_data):
    nan_key = "nan"
    for key, value in format_data.items():
        nan = value[nan_key]
        if nan is not None:
            df[key].fillna(nan, inplace=True)
    return df


def replace_dummy_with_nan(df: pd.DataFrame, format_dict: dict):
    """
    Replaces specific values in the DataFrame with NaN based on the given format dictionary.
    This is because sometimes, e.g. the DWD, fills in a dummy value which is actually nonsense.
    """
    for key, value in format_dict.items():
        if "nan" in value and key in df.columns:
            nan_values = value["nan"]
            if not isinstance(nan_values, list):
                nan_values = [nan_values]
            for nan_val in nan_values:
                df[key] = df[key].replace(nan_val, np.nan)
    return df


def evaluate_transformations(core_format, other_format):
    """
    Compares the units and core variables of two formats, and prints
    any required unit transformations.

    :param core_format: Dictionary representing the core format with
        keys as variable names and values containing unit information.
    :param other_format: Dictionary representing another format to be
        compared with the core format. It contains keys and values with
        'core_name' and 'unit' attributes.
    :raises ValueError: If a core variable in other_format doesn't fit
        the core variable format.
    """

    print("\nEvaluate format.")
    for key, value in other_format.items():
        if value["core_name"] in core_format.keys():
            # compare units
            if value["unit"] != core_format[value["core_name"]]["unit"]:
                print(
                    f"Unit transformation required for {value['core_name']} from"
                    f" {value['unit']} to {core_format[value['core_name']]['unit']}."
                )
        elif not value["core_name"]:
            pass
        else:
            raise ValueError(
                f"The core variable '{value['core_name']}' of import variable"
                f" {key} does not fit the core variable format"
            )


def select_entry_by_core_name(format_dict, core_name_to_match):
    for key, value in format_dict.items():
        if value["core_name"] == core_name_to_match:
            return value
