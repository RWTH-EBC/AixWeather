"""
This module contains auxiliary functions for data transformation, e.g. time shifts
"""

import pandas as pd

from aixweather.transformation_functions import auxiliary
from aixweather.imports.utils_import import MetaData


def create_pass_through_variables(
    df_shifted: pd.DataFrame,
    df_no_shift: pd.DataFrame,
    format: dict,
    transform_func,
    meta: MetaData,
):
    """
    This function adds unshifted data from the `df_no_shift` DataFrame to the `df_shifted` DataFrame to
    prevent unnecessary interpolation of values. It takes into account the required shifting and performs
    transformations. The appropriate pass-through variables (unshifted variables) are added to the dataframe
    with a suffix specifying the shifting that would be required for them. Calculated (transformed) variables
    are only added if the variables they were calculated from all have the same shifting (time of measurement).

    Args:
        df_shifted (pd.DataFrame): The DataFrame with shifted data.
        df_no_shift (pd.DataFrame): The DataFrame with unshifted data.
        format (dict): A dictionary specifying the format (required shifting) of the data.
        transform_func: The transformation function from the import2core data process.
        meta (MetaData): Metadata associated with the data.

    Returns:
        pd.DataFrame: The modified `df_shifted` DataFrame with added pass-through variables.
    """

    print("\nApply transformation for pass through variables.")
    # perform same transformation
    df_no_shift, meta.executed_transformations_no_shift = transform_func(df_no_shift)

    ### add unshifted variables present in the format_dict to the df
    for key, value in format.items():
        if (
            value["core_name"] not in meta.executed_transformations_no_shift.keys()
        ):  # imputed variables need the shift according to their used variables
            shift = value["time_of_meas_shift"]
            if shift is not None:
                df_shifted[f"{value['core_name']}_no_{shift}"] = df_no_shift[
                    value["core_name"]
                ]

    ### add unshifted variables that have been imputed from other variables
    for (
        desired_variable,
        used_variables,
    ) in meta.executed_transformations_no_shift.items():

        def get_shifts_of_used_variables(used_variables, meta):
            # get variables that have been used for transformation
            used_variables_shifts = {}
            for var in used_variables:
                if isinstance(var, str):
                    format_entry = auxiliary.select_entry_by_core_name(format, var)
                    if (
                        format_entry is not None
                        and var not in meta.executed_transformations_no_shift.keys()
                    ):  # use shift from format if var has not been calculated itself
                        used_variables_shifts.update(
                            {var: format_entry["time_of_meas_shift"]}
                        )
                    elif format_entry is None:
                        # then the used variable has been calculated itself and
                        # it is not in the format
                        # get the shifts of the variables used to calculate that used variable
                        used_variables_of_var = meta.executed_transformations_no_shift[
                            var
                        ]
                        used_variables_shifts_of_var = get_shifts_of_used_variables(
                            used_variables_of_var, meta
                        )
                        used_variables_shifts.update(used_variables_shifts_of_var)
            return used_variables_shifts

        used_variables_shifts = get_shifts_of_used_variables(used_variables, meta)

        # define vars of which the shift should be ignored for
        # validity checking, e.g. slowly changing variables
        vars_to_ignore_shift = []  # fill in the core names
        for var_to_ignore in vars_to_ignore_shift:
            used_variables_shifts.pop(var_to_ignore, None)

        # check whether they have all the same time shifting
        is_identical = len(set(used_variables_shifts.values())) == 1

        if not is_identical:
            # dont add to df
            print(
                f"Calculation of the non-shifted {desired_variable} is "
                f"not valid due non consistent "
                f"time of measurement (shifting) of the required "
                f"variables {used_variables_shifts}. "
                f"There wont be a pass-through for this variable. "
                f"Info: If used variables have been calculated themself "
                f"the shift of the used variables "
                f"for that calculation are checked."
            )
        else:
            # add to df
            shift = list(used_variables_shifts.values())[0]
            if shift is not None:
                df_shifted[f"{desired_variable}_no_{shift}"] = df_no_shift[
                    desired_variable
                ]

    return df_shifted


def _find_pass_through_core_names(columns: list, output_format: dict) -> list:
    """
    Identify pass-through variable names based on the output format and their column suffix.

    This function analyzes a list of column names and identifies those that represent pass-through
    core variables based on the provided output format. It takes into account suffix mappings
    to match the required shifting.

    Args:
        columns (list): A list of column names to analyze.
        output_format (dict): A dictionary specifying the desired format and shifting of the data.

    Returns:
        list: A list of column names representing pass-through variables that shall actually be passed through.
    """

    selected_columns = []
    suffix_mapping = {"_no_prec2ind": "ind2prec", "_no_foll2ind": "ind2foll"}

    for col in columns:
        core_name = col.split("_no_")[0]
        if core_name in output_format:
            suffix = col[len(core_name) :]
            if (
                suffix in suffix_mapping
                and output_format[core_name]["time_of_meas_shift"]
                == suffix_mapping[suffix]
            ):
                selected_columns.append(col)

    return selected_columns


def _find_and_apply_full_hour_shifts(df: pd.DataFrame, output_format: dict) -> tuple:
    """
    Find variables that require a full-hour shift to avoid double interpolation.

    This function identifies pass-through variables in the DataFrame `df` that are specified in the `output_format`
    to be shifted by a full hour in total. It performs the necessary full hour shift on these variables to prevent
    double interpolation.

    Args:
        df (pd.DataFrame): The DataFrame containing data to be shifted.
        output_format (dict): A dictionary specifying the desired format and shifting of the data.

    Returns:
        tuple: List of added pass-through variables and the modified DataFrame.
    """

    selected_columns = []
    suffix_mapping_forward = {"_no_prec2ind": "ind2foll"}
    suffix_mapping_backward = {"_no_foll2ind": "ind2prec"}

    for col in df.columns:
        core_name = col.split("_no_")[0]
        if core_name in output_format:
            suffix = col[len(core_name) :]
            if (
                suffix in suffix_mapping_forward
                and output_format[core_name]["time_of_meas_shift"]
                == suffix_mapping_forward[suffix]
            ):
                df.loc[:, col] = df[col].shift(periods=1, freq="H", axis=0)
                selected_columns.append(col)
            elif (
                suffix in suffix_mapping_backward
                and output_format[core_name]["time_of_meas_shift"]
                == suffix_mapping_backward[suffix]
            ):
                df.loc[:, col] = df[col].shift(periods=-1, freq="H", axis=0)
                selected_columns.append(col)

    return selected_columns, df


def pass_through_measurements_with_back_and_forth_interpolating(
    core2output_df: pd.DataFrame, format_outputter: dict
) -> pd.DataFrame:
    """
    Insert pass-through measurements to the output dataframe to
    avoid back-and-forth or double shifting interpolation.

    It deletes the double interpolated variables and inserts the pass-through ones where applicable.

    Args:
        core2output_df (pd.DataFrame): DataFrame containing core data in the process of core2outputfile.
        format_outputter (dict): Dictionary specifying the format of output data.

    Returns:
        pd.DataFrame: The modified `core2output_df` DataFrame with pass-through variables.
    """
    pass_trough_variables = _find_pass_through_core_names(
        core2output_df.columns, format_outputter
    )
    shift_full_hour_variables, core2output_df = _find_and_apply_full_hour_shifts(
        core2output_df, format_outputter
    )

    all_vars = pass_trough_variables + shift_full_hour_variables

    # delete interpolated variables and insert pass through or full hour shift variables
    for column_name in all_vars:
        core_name = column_name.split("_no")[0]
        # Drop the original variable
        core2output_df.drop(columns=[core_name], inplace=True)
        # Rename the "_noShift" variable by removing the suffix
        core2output_df.rename(columns={column_name: core_name}, inplace=True)

    return core2output_df
