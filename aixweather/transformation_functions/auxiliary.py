"""
includes auxiliary functions for data handling and transformation
"""
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def force_data_variable_convention(
    df: pd.DataFrame, format_desired: dict
) -> pd.DataFrame:
    """
    Ensure that all and only desired variable names are present and in correct order.

    Args:
        df (pd.DataFrame): The DataFrame containing the data to be formatted.
        format_desired (dict): A dictionary specifying the desired format with variable names as keys.

    Returns:
        pd.DataFrame: A DataFrame with filtered data in the desired format and order.
    """

    # filter existing df
    desired_var_names = set(format_desired.keys())
    df_core_var = df.loc[:, df.columns.isin(desired_var_names)]

    # Reindex the DataFrame to ensure all required columns exist and obey the order of columns
    df_core_var = df_core_var.reindex(columns=format_desired.keys())

    return df_core_var


def rename_columns(df: pd.DataFrame, format_dict: dict) -> pd.DataFrame:
    """
    Rename DataFrame columns based on the provided format dictionary.

    Args:
        df (pd.DataFrame): The DataFrame whose columns need to be renamed.
        format_dict (dict): A dictionary specifying the column renaming mapping,
                            with current column names as keys and desired names as values.

    Returns:
        pd.DataFrame: A DataFrame with renamed columns.
    """
    rename_map = {key: val["core_name"] for key, val in format_dict.items()}
    return df.rename(columns=rename_map)


def fill_nan_from_format_dict(df: pd.DataFrame, format_data: dict) -> pd.DataFrame:
    """
    Fill NaN values in a DataFrame based on the provided format data.

    Args:
        df (pd.DataFrame): The DataFrame containing the data to be processed.
        format_data (dict): A dictionary specifying NaN replacement values for columns,
                            with column names as keys and NaN replacement values as values.

    Returns:
        pd.DataFrame: A DataFrame with NaN values filled as per the format data.
    """
    nan_key = "nan"
    for key, value in format_data.items():
        nan = value[nan_key]
        if nan is not None:
            df[key].fillna(nan, inplace=True)
    return df


def replace_dummy_with_nan(df: pd.DataFrame, format_dict: dict) -> pd.DataFrame:
    """
    Replace specific values, or value ranges, in the DataFrame with NaN based on the given format
    dictionary. Reason: sometimes, e.g. the DWD, specifies a missing value with a dummy value
    like e.g. 99, which makes it hard to see where missing values are and might affect the
    simulation.

    Args:
        df (pd.DataFrame): The DataFrame to be processed.
        format_dict (dict): A dictionary specifying values to be replaced with NaN,
                            with column names as keys and corresponding dummy values as values.
                            Exact nans given through a float or int.
                            Value ranges given through a dictionary with the operator as key
                            and the threshold as value, e. g. {'<': 0}.

    Returns:
        pd.DataFrame: A DataFrame with specified values replaced by NaN.
    """

    for key, value in format_dict.items():
        if "nan" in value and key in df.columns:
            nan_values = value["nan"]
            if not isinstance(nan_values, list):
                nan_values = [nan_values]
            for nan_val in nan_values:
                # replace specified dummy values with NaN
                if not isinstance(nan_val, dict):
                    df[key] = df[key].replace(nan_val, np.nan)
                # replace specified value range with NaN
                else:
                    operator, threshold = list(nan_val.items())[0]

                    if operator == '<':
                        df.loc[df[key] < threshold, key] = np.nan
                    elif operator == '<=':
                        df.loc[df[key] <= threshold, key] = np.nan
                    elif operator == '>':
                        df.loc[df[key] > threshold, key] = np.nan
                    elif operator == '>=':
                        df.loc[df[key] >= threshold, key] = np.nan
                    elif operator == '==':
                        df.loc[df[key] == threshold, key] = np.nan
                    else:
                        raise ValueError(f"Unsupported operator: {operator}")

    return df


def evaluate_transformations(core_format: dict, other_format: dict):
    """
    Compare the units and core variables of two formats and print any required unit transformations.

    Args:
        core_format (dict): A dictionary representing the core format with keys as variable names and values
                            containing unit information.
        other_format (dict): A dictionary representing another format to be compared with the core format.
                            It contains keys and values with 'core_name' and 'unit' attributes.

    Raises:
        ValueError: If a core variable in other_format doesn't match the core variable format.
    """

    logger.debug("Evaluate format.")
    for key, value in other_format.items():
        if value["core_name"] in core_format.keys():
            # compare units
            if value["unit"] != core_format[value["core_name"]]["unit"]:
                logger.debug(
                    "Unit transformation required for %s from %s to %s.",
                    value['core_name'], value['unit'],
                    core_format[value['core_name']]['unit']
                )
        elif not value["core_name"]:
            pass
        else:
            raise ValueError(
                f"The core variable '{value['core_name']}' of import variable"
                f" {key} does not fit the core variable format"
            )


def select_entry_by_core_name(format_dict: dict, core_name_to_match: str):
    """
    Select an entry from a format dictionary based on the specified core name.

    Args:
        format_dict (dict): A dictionary to search for the entry.
        core_name_to_match (str): The core name to match in the dictionary values.

    Returns:
        dict: The dictionary entry matching the specified core name, or None if not found.
    """
    for key, value in format_dict.items():
        if value["core_name"] == core_name_to_match:
            return value
