import datetime as dt
import pandas as pd

from abc import ABC, abstractmethod

from AixWeather.imports.DWD import (
    import_DWD_historical,
    import_DWD_forecast,
    import_meta_DWD_historical,
    import_meta_DWD_forecast,
)
from AixWeather.imports.ERC import import_ERC, import_meta_from_ERC
from AixWeather.imports.TRY import load_try_from_file, load_try_meta_from_file
from AixWeather.imports.EPW import load_epw_from_file, load_epw_meta_from_file
from AixWeather.imports.custom_file import load_custom_meta_data, load_custom_from_file
from AixWeather.transformation_to_core_data.DWD import (
    DWD_historical_to_core_data,
    DWD_forecast_2_core_data,
)
from AixWeather.transformation_to_core_data.ERC import ERC_to_core_data
from AixWeather.transformation_to_core_data.TRY import TRY_to_core_data
from AixWeather.transformation_to_core_data.EPW import EPW_to_core_data
from AixWeather.transformation_to_core_data.custom_file import custom_to_core_data
from AixWeather.core_data_format_2_output_file.unconverted_to_x import (
    to_pickle,
    to_json,
    to_csv,
)
from AixWeather.core_data_format_2_output_file.to_mos_TMY3 import to_mos
from AixWeather.core_data_format_2_output_file.to_epw_energyplus import to_epw


class ProjectClassGeneral(ABC):
    """
    An abstract base class representing a general project.
    For each origin of weather data a project class inherits from this class.
    """

    def __init__(self, **kwargs):
        # User-settable attributes
        self.fillna = kwargs.get("fillna", True) # defines whether nan should be filled in the output formats

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
        if value is not None:
            # only real pd.NA values
            for column in value.columns:
                value[column] = pd.to_numeric(
                    value[column], errors="coerce"
                )  # force strings to be NaN
            self._core_data = value

    @abstractmethod
    def import_data(self):
        pass

    @abstractmethod
    def data_2_core_data(self):
        pass

    # core_data_format_2_output_file
    def core_2_mos(self):
        self.output_df_mos = to_mos(
            self.core_data, self.meta_data, self.start, self.end, self.fillna
        )

    def core_2_epw(self):
        self.output_df_epw = to_epw(
            self.core_data, self.meta_data, self.start, self.end, self.fillna
        )

    def core_2_csv(self):
        self.output_df_csv = to_csv(self.core_data, self.meta_data)

    def core_2_json(self):
        self.output_df_json = to_json(self.core_data, self.meta_data)

    def core_2_pickle(self):
        self.output_df_pickle = to_pickle(self.core_data, self.meta_data)

class ProjectClassDWDHistorical(ProjectClassGeneral):
    def __init__(self, start: dt.datetime, end: dt.datetime, station: str, **kwargs):
        super().__init__(start=start, end=end, **kwargs)
        self.station = station

    # imports
    def import_data(self):
        self.meta_data = import_meta_DWD_historical(station=self.station)
        self.imported_data = import_DWD_historical(
            self.start - dt.timedelta(days=1), self.station
        )  # pull more data for better interpolation

    # transformation_2_core_data_DWD_Historical
    def data_2_core_data(self):
        self.core_data = DWD_historical_to_core_data(
            self.imported_data,
            self.start - dt.timedelta(days=1),
            self.end + dt.timedelta(days=1),
            self.meta_data,
        )


class ProjectClassDWDForecast(ProjectClassGeneral):
    def __init__(self, station: str, **kwargs):
        super().__init__(**kwargs)
        self.station = station

    # imports
    def import_data(self):
        self.meta_data = import_meta_DWD_forecast(self.station)
        self.imported_data = import_DWD_forecast(self.station)

    def data_2_core_data(self):
        self.core_data = DWD_forecast_2_core_data(self.imported_data, self.meta_data)
        self.start = self.core_data.index[0]
        self.end = self.core_data.index[-1]


class ProjectClassERC(ProjectClassGeneral):
    def __init__(self, start: dt.datetime, end: dt.datetime, cred: tuple = None, **kwargs):
        super().__init__(start=start, end=end, **kwargs)
        self.cred = cred
        self.start_hour_earlier = start - dt.timedelta(hours=2)
        self.end_hour_later = end + dt.timedelta(hours=2)

    def import_data(self):
        self.imported_data = import_ERC(
            self.start_hour_earlier, self.end_hour_later, self.cred
        )
        self.meta_data = import_meta_from_ERC()

    def data_2_core_data(self):
        self.core_data = ERC_to_core_data(self.imported_data, self.meta_data)


class ProjectClassTRY(ProjectClassGeneral):
    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)
        self.path = path

    # imports
    def import_data(self):
        self.imported_data = load_try_from_file(path=self.path)
        self.meta_data = load_try_meta_from_file(path=self.path)

    # transformation_2_core_data_TRY
    def data_2_core_data(self):
        self.core_data = TRY_to_core_data(self.imported_data, self.meta_data)
        self.start = self.core_data.index[0]
        self.end = self.core_data.index[-1]


class ProjectClassEPW(ProjectClassGeneral):
    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)
        self.path = path

    # imports
    def import_data(self):
        self.imported_data = load_epw_from_file(path=self.path)
        self.meta_data = load_epw_meta_from_file(path=self.path)

    # transformation_2_core_data_TRY
    def data_2_core_data(self):
        self.core_data = EPW_to_core_data(self.imported_data, self.meta_data)
        self.start = self.core_data.index[0]
        self.end = self.core_data.index[-1]


class ProjectClassCustom(ProjectClassGeneral):
    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)
        self.path = path

    # imports
    def import_data(self):
        self.imported_data = load_custom_from_file(path=self.path)
        self.meta_data = load_custom_meta_data(path=self.path)

    # transformation_2_core_data_TRY
    def data_2_core_data(self):
        self.core_data = custom_to_core_data(self.imported_data, self.meta_data)
        self.start = self.core_data.index[0]  # or define in init
        self.end = self.core_data.index[-1]  # or define in init
