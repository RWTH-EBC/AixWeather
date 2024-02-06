"""
change this file to your custom requirements (only import and perform as
little preprocessing as possible)
"""

from aixweather.imports.utils_import import MetaData


def load_custom_meta_data():
    """
    define or load your meta data here
    """

    meta = MetaData()
    meta.station_name = ""
    meta.input_source = f"Custom data"
    meta.altitude = ""
    meta.longitude = ""
    meta.latitude = ""

    return meta


def load_custom_from_file(path):
    """
    Import data from file and convert them into df

    Args:
        path: absolute path to file

    Returns:
        pd.Dataframe: as raw as possible
    """

    ### load file to Dataframe

    ### convert timestamp to datetime and set as index

    ### return data frame
    return "DataFrame"
