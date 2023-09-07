import os

# format of the core_data
# time of measurement is always at indicated time
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

# creates the path to the root directory to be used in other modules
ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))

# local temporary folder
local_folder_temp = os.path.join(ROOT_DIR, "temp_local")

def result_folder_path() -> str:
    folder_path = os.path.join(f"{ROOT_DIR}", "results")
    return folder_path

def results_file_path(filename: str, folder_path: str = None) -> str:
    """
    create a path to a results file

    Args:
        filename: name of file
        folder_path: path to result folder

    Returns:
        str: path to result file
    """
    # if required specify folder_path e.g. for Django WebApp
    if folder_path is None:
        folder_path = result_folder_path()

    # Ensure that the results folder exists
    os.makedirs(folder_path, exist_ok=True)

    # create file path
    filepath = os.path.join(folder_path, filename)
    return filepath
