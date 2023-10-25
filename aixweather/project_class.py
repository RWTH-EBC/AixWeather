"""This module contains the central project classes which are used by the user."""

from abc import ABC, abstractmethod
import datetime as dt
import pandas as pd

from aixweather.imports.DWD import (
    import_DWD_historical,
    import_DWD_forecast,
    import_meta_DWD_historical,
    import_meta_DWD_forecast,
)
from aixweather.imports.ERC import import_ERC, import_meta_from_ERC
from aixweather.imports.TRY import load_try_from_file, load_try_meta_from_file
from aixweather.imports.EPW import load_epw_from_file, load_epw_meta_from_file
from aixweather.imports.custom_file import load_custom_meta_data, load_custom_from_file
from aixweather.transformation_to_core_data.DWD import (
    DWD_historical_to_core_data,
    DWD_forecast_2_core_data,
)
from aixweather.transformation_to_core_data.ERC import ERC_to_core_data
from aixweather.transformation_to_core_data.TRY import TRY_to_core_data
from aixweather.transformation_to_core_data.EPW import EPW_to_core_data
from aixweather.transformation_to_core_data.custom_file import custom_to_core_data
from aixweather.core_data_format_2_output_file.unconverted_to_x import (
    to_pickle,
    to_json,
    to_csv,
)
from aixweather.core_data_format_2_output_file.to_mos_TMY3 import to_mos
from aixweather.core_data_format_2_output_file.to_epw_energyplus import to_epw


class ProjectClassGeneral(ABC):
    """
    An abstract base class representing a general project.

    For each source of weather data, a project class should inherit from this class
    and implement specific methods for data import and transformation.

    Attributes:
        fillna (bool): A flag indicating whether NaN values should be filled
            in the output formats.
        abs_result_folder_path (str): Optionally define the absolute path to
            the desired export location.
        start (pd.Timestamp or None): The start date of the project data
            (sometimes inferred by the inheriting class).
        end (pd.Timestamp or None): The end date of the project data.

    Properties:
        imported_data (pd.DataFrame): The imported weather data.
        core_data (pd.DataFrame): The weather data in a standardized core
            format.
        output_df_<outputformat> (pd.DataFrame): The output data frame
            (name depends on output format).
        meta_data: Metadata associated with weather data origin.

    Methods:
        import_data(): An abstract method to import data from the specific
            source.
        data_2_core_data(): An abstract method to transform imported data into
            core data format.
        core_2_mos(): Convert core data to MOS format.
        core_2_epw(): Convert core data to EPW format.
        core_2_csv(): Convert core data to CSV format.
        core_2_json(): Convert core data to JSON format.
        core_2_pickle(): Convert core data to Pickle format.
    """

    def __init__(self, **kwargs):
        # User-settable attributes
        self.fillna = kwargs.get(
            "fillna", True
        )  # defines whether nan should be filled in the output formats
        self.abs_result_folder_path = kwargs.get("abs_result_folder_path", None)

        # User-settable or placeholder depending on data origin
        self.start = kwargs.get("start", None)
        self.end = kwargs.get("end", None)

        # Placeholder attributes (set during execution)
        self.imported_data: pd.DataFrame = None
        self.core_data: pd.DataFrame = None
        self.output_data_df: pd.DataFrame = None
        self.meta_data = None

    @property
    def core_data(self):
        return self._core_data

    @core_data.setter
    def core_data(self, value: pd.DataFrame):
        """Makes sure the core data data types are correct."""
        if value is not None:
            for column in value.columns:
                # only real pd.NA values
                # force strings to be NaN
                value[column] = pd.to_numeric(value[column], errors="coerce")
                # round floats for unit test compatibility across different machines
                digits_2_round = 5
                if value[column].dtype == "float":
                    value[column] = value[column].round(digits_2_round)

            self._core_data = value

    @abstractmethod
    def import_data(self):
        """Abstract function to import weather data."""
        pass

    @abstractmethod
    def data_2_core_data(self):
        """Abstract function to convert the imported data to core data."""
        pass

    # core_data_format_2_output_file
    def core_2_mos(self):
        """Convert core data to .mos file"""
        self.output_data_df = to_mos(
            self.core_data,
            self.meta_data,
            self.start,
            self.end,
            self.fillna,
            self.abs_result_folder_path,
        )

    def core_2_epw(self):
        """Convert core data to .epw file"""
        self.output_data_df = to_epw(
            self.core_data,
            self.meta_data,
            self.start,
            self.end,
            self.fillna,
            self.abs_result_folder_path,
        )

    def core_2_csv(self):
        """Convert core data to .csv file"""
        self.output_data_df = to_csv(
            self.core_data, self.meta_data, self.abs_result_folder_path
        )

    def core_2_json(self):
        """Convert core data to .json file"""
        self.output_data_df = to_json(
            self.core_data, self.meta_data, self.abs_result_folder_path
        )

    def core_2_pickle(self):
        """Convert core data pickle file"""
        self.output_data_df = to_pickle(
            self.core_data, self.meta_data, self.abs_result_folder_path
        )


class ProjectClassDWDHistorical(ProjectClassGeneral):
    """
    A class representing a project for importing and processing historical weather data
    from DWD (Deutscher Wetterdienst).

    For common attributes, properties, and methods, refer to the base class.

    Attributes:
        station (str): The identifier of the DWD weather station associated with the data.
    """

    def __init__(self, start: dt.datetime, end: dt.datetime, station: str, **kwargs):
        super().__init__(start=start, end=end, **kwargs)
        self.station = station

    # imports
    def import_data(self):
        """override abstract function"""
        self.meta_data = import_meta_DWD_historical(station=self.station)
        self.imported_data = import_DWD_historical(
            self.start - dt.timedelta(days=1), self.station
        )  # pull more data for better interpolation

    # transformation_2_core_data_DWD_Historical
    def data_2_core_data(self):
        """override abstract function"""
        self.core_data = DWD_historical_to_core_data(
            self.imported_data,
            self.start - dt.timedelta(days=1),
            self.end + dt.timedelta(days=1),
            self.meta_data,
        )


class ProjectClassDWDForecast(ProjectClassGeneral):
    """
    A class representing a project for importing and processing weather forecast data
    from DWD (Deutscher Wetterdienst).

    For common attributes, properties, and methods, refer to the base class.

    Attributes:
        station (str): The identifier of the KML grid associated with the forecast data.
    """

    def __init__(self, station: str, **kwargs):
        super().__init__(**kwargs)
        self.station = station

    # imports
    def import_data(self):
        """override abstract function"""
        self.meta_data = import_meta_DWD_forecast(self.station)
        self.imported_data = import_DWD_forecast(self.station)

    def data_2_core_data(self):
        """override abstract function"""
        self.core_data = DWD_forecast_2_core_data(self.imported_data, self.meta_data)
        self.start = self.core_data.index[0]
        self.end = self.core_data.index[-1]


class ProjectClassERC(ProjectClassGeneral):
    """
    A class representing a project for importing and processing weather data
    from the ERC (Energy Research Center).

    For common attributes, properties, and methods, refer to the base class.

    Attributes:
        cred (tuple): A tuple containing credentials or authentication information for accessing
        the data source.
    """

    def __init__(
        self, start: dt.datetime, end: dt.datetime, cred: tuple = None, **kwargs
    ):
        super().__init__(start=start, end=end, **kwargs)
        self.cred = cred
        self.start_hour_earlier = start - dt.timedelta(hours=2)
        self.end_hour_later = end + dt.timedelta(hours=2)

    def import_data(self):
        """override abstract function"""
        self.imported_data = import_ERC(
            self.start_hour_earlier, self.end_hour_later, self.cred
        )
        self.meta_data = import_meta_from_ERC()

    def data_2_core_data(self):
        """override abstract function"""
        self.core_data = ERC_to_core_data(self.imported_data, self.meta_data)


class ProjectClassTRY(ProjectClassGeneral):
    """
    A class representing a project for importing and processing weather data
    from TRY (Test Reference Year) format.

    For common attributes, properties, and methods, refer to the base class.

    Attributes:
        path (str): The absolute file path to the TRY weather data.
    """

    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)
        self.path = path

    # imports
    def import_data(self):
        """override abstract function"""
        self.imported_data = load_try_from_file(path=self.path)
        self.meta_data = load_try_meta_from_file(path=self.path)

    # transformation_2_core_data_TRY
    def data_2_core_data(self):
        """override abstract function"""
        self.core_data = TRY_to_core_data(self.imported_data, self.meta_data)
        self.start = self.core_data.index[0]
        self.end = self.core_data.index[-1]


class ProjectClassEPW(ProjectClassGeneral):
    """
    A class representing a project for importing and processing weather data
    from EPW (EnergyPlus Weather) format.

    For common attributes, properties, and methods, refer to the base class.

    Attributes:
        path (str): The absolute file path to the EPW weather data.
    """

    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)
        self.path = path

    # imports
    def import_data(self):
        """override abstract function"""
        self.imported_data = load_epw_from_file(path=self.path)
        self.meta_data = load_epw_meta_from_file(path=self.path)

    # transformation_2_core_data_TRY
    def data_2_core_data(self):
        """override abstract function"""
        self.core_data = EPW_to_core_data(self.imported_data, self.meta_data)
        self.start = self.core_data.index[0]
        self.end = self.core_data.index[-1]


class ProjectClassCustom(ProjectClassGeneral):
    """
    A class representing a project for importing and processing custom weather data.
    Modify this class and its functions to create your own weather data pipeline
    and consider to create a pull request to add the pipeline to the repository.

    For common attributes, properties, and methods, refer to the base class.

    Attributes:
        path (str): The file path to the custom weather data.
    """

    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)
        self.path = path

    # imports
    def import_data(self):
        """override abstract function"""
        self.imported_data = load_custom_from_file(path=self.path)
        self.meta_data = load_custom_meta_data()

    # transformation_2_core_data_TRY
    def data_2_core_data(self):
        """override abstract function"""
        self.core_data = custom_to_core_data(self.imported_data, self.meta_data)
        self.start = self.core_data.index[0]  # or define in init
        self.end = self.core_data.index[-1]  # or define in init
