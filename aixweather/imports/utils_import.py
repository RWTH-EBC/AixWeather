"""
includes a class that reads metadata from weather station
"""
import warnings

from unidecode import unidecode


class MetaData:
    """
    A class for storing metadata information about a weather station.

    Attributes:
        station_name (str): The name of the weather station.
        station_id (str): The ID (DWD or DWD MOSMIX ID) of the weather station.
        altitude (float): The altitude of the weather station in meters.
        latitude (float): The latitude of the weather station in degree.
        longitude (float): The longitude of the weather station in degree.
        timezone (int): The timezone relative to UTC. E.g. -1 is UTC-1, 0 is UTC, etc.
        input_source (str): The source of input data for the station.
    """
    def __init__(self, **kwargs: str):
        self._station_name: str = "UnknownStationName"
        self.station_id: str = "UnknownStationID"
        self._altitude: float = None
        self._latitude: float = None
        self._longitude: float = None
        self._timezone: int = 0  # Used for export
        self._imported_timezone: int = 0
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
        self._altitude = round(_ensure_float(value), 5)

    @property
    def latitude(self) -> float:
        return self._latitude

    @latitude.setter
    def latitude(self, value: float) -> None:
        self._latitude = round(_ensure_float(value), 5)

    @property
    def longitude(self) -> float:
        return self._longitude

    @longitude.setter
    def longitude(self, value: float) -> None:
        self._longitude = round(_ensure_float(value), 5)

    @property
    def timezone(self) -> float:
        return self._timezone

    @timezone.setter
    def timezone(self, value: float) -> None:
        _check_timezone_bounds(value)
        if value != self._imported_timezone:
            warnings.warn(
                f"You are changing the imported timezone by {self._imported_timezone - value} hours. "
                "Ensure your other simulation input times also use this shift and check results."
            )
        self._timezone = value

    def set_imported_timezone(self, value: float) -> None:
        _check_timezone_bounds(value)
        self._timezone = value
        self._imported_timezone = value


def _check_timezone_bounds(value: float) -> None:
    if not isinstance(value, (float, int)):
        raise TypeError("Given timezone is not a valid int or float")
    if value < -12 or value > 14:
        raise ValueError("Given timezone is outside -12 and +14")


def _ensure_float(value):
    if value is not None:
        try:
            return float(value)
        except:
            raise ValueError(f"Value must be of type float, not {type(value)}")
