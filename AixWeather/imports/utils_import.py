"""
includes a class that reads metadata from weather station
"""

from unidecode import unidecode


class MetaData:
    """
    A class for storing metadata information about a weather station.

    Attributes:
        station_name (str): The name of the weather station.
        station_id (str): The ID (DWD or KML grid ID) of the weather station.
        altitude (float): The altitude of the weather station in meters.
        latitude (float): The latitude of the weather station in degree.
        longitude (float): The longitude of the weather station in degree.
        input_source (str): The source of input data for the station.
    """
    def __init__(self, **kwargs: str):
        self._station_name: str = "UnknownStationName"
        self.station_id: str = "UnknownStationID"
        self._altitude: float = None
        self._latitude: float = None
        self._longitude: float = None
        self.input_source: str = "UnknownInputSource"

        self.__dict__.update(kwargs)

    @property
    def station_name(self):
        return self._station_name

    @station_name.setter
    def station_name(self, value):
        """avoid special chars"""
        self._station_name = unidecode(value)

    @property
    def altitude(self) -> float:
        return self._altitude

    @altitude.setter
    def altitude(self, value: float) -> None:
        self._altitude = round(self._ensure_float(value), 5)

    @property
    def latitude(self) -> float:
        return self._latitude

    @latitude.setter
    def latitude(self, value: float) -> None:
        self._latitude = round(self._ensure_float(value), 5)

    @property
    def longitude(self) -> float:
        return self._longitude

    @longitude.setter
    def longitude(self, value: float) -> None:
        self._longitude = round(self._ensure_float(value), 5)

    def _ensure_float(self, value):
        if value is not None:
            try:
                return float(value)
            except:
                raise ValueError(f"Value must be of type float, not {type(value)}")
