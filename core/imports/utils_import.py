"""
includes a class that reads metadata from weather station
"""

from unidecode import unidecode


class MetaData:
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
        self._altitude = self._ensure_float(value)

    @property
    def latitude(self) -> float:
        return self._latitude

    @latitude.setter
    def latitude(self, value: float) -> None:
        self._latitude = self._ensure_float(value)

    @property
    def longitude(self) -> float:
        return self._longitude

    @longitude.setter
    def longitude(self, value: float) -> None:
        self._longitude = self._ensure_float(value)

    def _ensure_float(self, value):
        if value is not None:
            try:
                return float(value)
            except:
                raise ValueError(f"Value must be of type float, not {type(value)}")
