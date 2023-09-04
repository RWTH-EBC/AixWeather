"""
This module includes variable transformations and functions
to calculate variables from given values
"""

import pandas as pd
import numpy as np

import pvlib

from core.imports.utils_import import MetaData


def approximate_opaque_from_total_skycover(total_sky_cover):
    opaque_sky_cover = total_sky_cover
    return opaque_sky_cover


def calculate_dew_point_temp(dry_bulb_temp, rel_hum):
    """Calculate dew point temperature -> fairly accurate for
       humidity above 50% maybe get better formula!?
    param:
        df/float:    DryBulbTemp in °C
        df/float:    RelHum in %
    return:
        df/float:    DewPointTemp in °C
    """
    dew_point_temp = dry_bulb_temp - (100 - rel_hum) / 5
    return dew_point_temp


def calculate_direct_horizontal_radiation(glob_hor_rad, diff_hor_rad):
    """Calculate direct horizontal radiation by substracting
    global horizontal radiation with diffuse horizontal radiation

    Checked by Martin Rätz (08.08.2023)

    param:
        df/float:    GlobHorRad in Wh/m^2
        df/float:    DiffHorRad in Wh/m^2
    return:
        df/float:    direct horizontal radiation in Wh/m^2
    """
    dir_hor_rad = glob_hor_rad - diff_hor_rad
    if isinstance(dir_hor_rad, pd.Series):
        dir_hor_rad.clip(0, inplace=True)
    else:
        if dir_hor_rad < 0:
            dir_hor_rad = 0
    return dir_hor_rad


def calculate_global_horizontal_radiation(dir_hor_rad, diff_hor_rad):
    """Calculate Global horizontal radiation on a horizontal plane
    by adding direct horizontal radiation with diffuse horizontal radiation.

    Checked by Martin Rätz (08.08.2023) using:
    https://pvpmc.sandia.gov/modeling-steps/1-weather-design-inputs/irradiance-insolation/global-horizontal-irradiance/
    param:
        df/float:    DirHorRad in Wh/m^2
        df/float:    DiffHorRad in Wh/m^2
    return:
        df/float:    Global normal radiation in Wh/m^2
    """
    glob_hor_rad = dir_hor_rad + diff_hor_rad

    # if value < 0 set as 0
    if isinstance(glob_hor_rad, pd.Series):
        glob_hor_rad.clip(0, inplace=True)
    else:
        if glob_hor_rad < 0:
            glob_hor_rad = 0

    return glob_hor_rad


def calculate_horizontal_infrared_radiation(dry_bulb_temp, dew_point_temp, opaque_sky_cover):
    """
    Calculate horizontal infrared radiation according to:
    https://www.energyplus.net/sites/default/files/docs/site_v8.3.0/EngineeringReference/05-Climate/index.html
    by using sky emissivity according to:
    https://www.energyplus.net/sites/default/files/docs/site_v8.3.0/EngineeringReference/05-Climate/index.html

    param:
        df/float:    DryBulbTemp in °C
        df/float:    DewPointTemp in °C
        df/float:    OpaqueSkyCover in tenths
    return:
        df/float:    HorInfra in Wh/m^2
    """
    # change to Kelvin
    dry_bulb_temp = dry_bulb_temp + 273.15
    dew_point_tem = dew_point_temp + 273.15

    sky_emissivity = (0.787 + 0.764 * np.log(dew_point_tem / 273.0)) * (
            1.0
            + 0.0224 * opaque_sky_cover
            - 0.0035 * np.power(opaque_sky_cover, 2)
            + 0.00028 * np.power(opaque_sky_cover, 3)
    )
    """equation 3 from Sky Radiation Modeling
    https://www.energyplus.net/sites/default/files/docs/site_v8.3.0/
    EngineeringReference/05-Climate/index.html"""

    hor_infra = sky_emissivity * 5.6697 * np.power(10.0, -8.0) * np.power(dry_bulb_temp, 4)
    """equation 2 from Sky Radiation Modeling 
    https://www.energyplus.net/sites/default/files/docs/site_v8.3.0/EngineeringReference/05-Climate/index.html
    """
    return hor_infra


def calculate_normal_from_horizontal_direct_radiation(
    latitude: float,
    longitude: float,
    utc_time: pd.DatetimeIndex,
    direct_horizontal_radiation: pd.Series,
):
    """
    Calculates the Direct Normal Irradiance (DNI) from Direct Horizontal Irradiance (DHI).

    Parameters:
        latitude (float): The latitude of the location in degrees.
        longitude (float): The longitude of the location in degrees.
        utc_time (pd.DatetimeIndex): The timestamps for which the DNI is to be calculated, in UTC.
        direct_horizontal_radiation (pd.Series): The Direct Horizontal Irradiance (DHI) in [W/m^2]

    Returns:
        pd.Series: The calculated Direct Normal Irradiance (DNI) in W/m^2 for each timestamp.
        Values will be set to zero when the sun is below 5° angle from the horizon.
    """

    # Calculate the solar zenith angle for each time
    solar_position = pvlib.solarposition.get_solarposition(
        utc_time.tz_localize("UTC"), latitude, longitude
    )
    solar_position.index = solar_position.index.tz_localize(None)
    zenith_angle_deg = solar_position["zenith"]

    # Calculate the Direct Normal Irradiance (DNI) for each time
    zenith_angle_rad = zenith_angle_deg * (np.pi / 180)  # Convert to radians
    dni = direct_horizontal_radiation / np.cos(zenith_angle_rad)

    # Set values to zero when the sun is below 5° angle from the horizon
    dni = np.where(zenith_angle_deg > 85, 0, dni)

    return dni


# wrapping functions ------------------------------------------
def robust_transformation(
    df: pd.DataFrame, desired_variable: str, transformation_function, *args: str
):
    """
    Applies a transformation function to calculate the desired variable in the DataFrame
    if the variable is missing or contains only NaN values. Skips the transformation if
    any required column (specified in args) is missing to perform the calculation.

    Parameters:
        df: DataFrame containing the data.
        desired_variable: Name of the variable to which the transformation should be applied.
        transformation_function: Function to apply to the desired variable.
        *args: Additional arguments required for the transformation function. Can be column
               names (str) or other values (all other types).

    Returns:
        DataFrame with the transformation applied to the desired variable.
    """
    # Feed back whether calculation was done and with which variables
    calc_status = {}

    # Check if the desired variable is missing or contains only NaN values
    if desired_variable not in df.columns or df[desired_variable].isna().all():
        # refactor args to account for strings to get the column of the df and pure objects
        new_args = list()
        args_of_columns = list()  # get only strings of args that are column names
        for arg in args:
            # if arg is a column of the df, the new arg should be the column values
            if isinstance(arg, str):
                if arg in df.columns:
                    # if contains only NaN values
                    if df[arg].isna().all():
                        print(
                            f"The required variable {arg} has only nan, "
                            f"calculation of {desired_variable} aborted."
                        )
                        return df, calc_status
                    new_args.append(df[arg])
                    args_of_columns.append(arg)
                else:
                    print(
                        f"The required variable {arg} is not in the dataframes "
                        f"columns, calculation of {desired_variable} aborted."
                    )
                    return df, calc_status
            else:
                # if arg is an object, e.g. from meta_data, add it directly
                new_args.append(arg)

        # Apply transformation if variables are available
        df[desired_variable] = transformation_function(*new_args)
        print(f"Calculated {desired_variable} from {args_of_columns}.")

        # Feed back whether calculation was done and with which variables
        calc_status = {desired_variable: args_of_columns}

    return df, calc_status


def variable_transform_all(df, meta: MetaData):
    """
    You can add all variable transformations here.
    Respect a meaningful order.

    Transforms and computes missing variables for the given dataframe based on
    specified calculations.
    This function performs multiple transformations on the dataframe to calculate missing variables.
    The applied calculations for each variable are tracked in the 'calc_overview' dictionary.

    Returns:
    - DataFrame: Transformed dataframe with computed variables.
    - dict: A dictionary ('calc_overview') tracking the calculations applied to the dataframe.
    """
    # track if calculations are applied
    calc_overview = {}

    ### calculate missing variables for core data format if required and if possible
    df, calc_status = robust_transformation(
        df, "OpaqueSkyCover", approximate_opaque_from_total_skycover, "TotalSkyCover"
    )
    calc_overview.update(calc_status)
    df, calc_status = robust_transformation(
        df, "DewPointTemp", calculate_dew_point_temp, "DryBulbTemp", "RelHum"
    )
    calc_overview.update(calc_status)
    df, calc_status = robust_transformation(
        df, "DirHorRad", calculate_direct_horizontal_radiation, "GlobHorRad", "DiffHorRad"
    )
    calc_overview.update(calc_status)
    df, calc_status = robust_transformation(
        df,
        "DirNormRad",
        calculate_normal_from_horizontal_direct_radiation,
        meta.latitude,
        meta.longitude,
        df.index,
        "DirHorRad",
    )
    calc_overview.update(calc_status)
    df, calc_status = robust_transformation(
        df,
        "HorInfra",
        calculate_horizontal_infrared_radiation,
        "DryBulbTemp",
        "DewPointTemp",
        "OpaqueSkyCover",
    )
    calc_overview.update(calc_status)

    return df, calc_overview
