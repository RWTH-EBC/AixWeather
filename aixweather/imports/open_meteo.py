"""
imports weather data from the Open-Meteo API (https://open-meteo.com)
"""

import datetime as dt
import logging
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pandas as pd
import requests

from aixweather.imports.utils_import import MetaData

logger = logging.getLogger(__name__)

# API endpoints, see https://open-meteo.com/en/docs
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
# Open-Meteo is free for non-commercial use. Commercial use requires a subscription
# (api_key), which is served through separate endpoints, see
# https://open-meteo.com/en/pricing
CUSTOMER_URLS = {
    ARCHIVE_URL: "https://customer-archive-api.open-meteo.com/v1/archive",
    FORECAST_URL: "https://customer-api.open-meteo.com/v1/forecast",
}

# first day the historical (ERA5 based) archive provides data for
ARCHIVE_FIRST_DAY = dt.date(1940, 1, 1)
# limits of the forecast API
MAX_FORECAST_DAYS = 16
MAX_PAST_DAYS = 92

# request settings
_TIMEOUT = 60  # seconds until a request is considered as failed
_RETRIES = 3  # number of tries before the pull is given up

# Hourly variables to be pulled. They must match the keys of the respective format
# dictionary in aixweather.transformation_to_core_data.open_meteo, which is
# ensured by a unit test.
HOURLY_VARIABLES_HISTORICAL = [
    "temperature_2m",
    "relative_humidity_2m",
    "dew_point_2m",
    "surface_pressure",
    "cloud_cover",
    "wind_speed_10m",
    "wind_direction_10m",
    "shortwave_radiation",
    "diffuse_radiation",
    "direct_radiation",
    "direct_normal_irradiance",
    "terrestrial_radiation",
    "precipitation",
    "soil_temperature_0_to_7cm",
    "soil_temperature_7_to_28cm",
]
HOURLY_VARIABLES_FORECAST = [
    "temperature_2m",
    "relative_humidity_2m",
    "dew_point_2m",
    "surface_pressure",
    "cloud_cover",
    "visibility",
    "wind_speed_10m",
    "wind_direction_10m",
    "shortwave_radiation",
    "diffuse_radiation",
    "direct_radiation",
    "direct_normal_irradiance",
    "terrestrial_radiation",
    "precipitation",
    "soil_temperature_6cm",
    "soil_temperature_18cm",
    "soil_temperature_54cm",
]


def import_open_meteo_historical(
    start: dt.datetime,
    end: dt.datetime,
    latitude: float,
    longitude: float,
    api_key: str = None,
) -> pd.DataFrame:
    """
    Pull historical (reanalysis) weather data from the Open-Meteo archive API
    (https://open-meteo.com/en/docs/historical-weather-api) and format them into a dataframe.

    The data is pulled in UTC, as required for the core data format.

    Args:
        start: Datetime object defining the first day to be pulled.
        end: Datetime object defining the last day to be pulled.
        latitude: Latitude of the desired location in degree.
        longitude: Longitude of the desired location in degree.
        api_key: Optional Open-Meteo API key, required for commercial use.

    Returns:
        pd.DataFrame: Weather data from Open-Meteo that is as raw as possible.
    """
    _check_coordinates(latitude, longitude)
    start_date, end_date = _limit_archive_dates(start.date(), end.date())

    data = _request_open_meteo(
        url=ARCHIVE_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "hourly": ",".join(HOURLY_VARIABLES_HISTORICAL),
            # request UTC and m/s to match the core data format
            "timezone": "GMT",
            "wind_speed_unit": "ms",
        },
        api_key=api_key,
    )

    return _hourly_to_dataframe(data)


def import_open_meteo_forecast(
    latitude: float,
    longitude: float,
    forecast_days: int = 7,
    past_days: int = 0,
    api_key: str = None,
) -> pd.DataFrame:
    """
    Pull weather forecast data from the Open-Meteo forecast API
    (https://open-meteo.com/en/docs) and format them into a dataframe.

    The data is pulled in UTC, as required for the core data format.

    Args:
        latitude: Latitude of the desired location in degree.
        longitude: Longitude of the desired location in degree.
        forecast_days: Number of days to be forecasted (0 to 16).
        past_days: Number of past days to be pulled additionally (0 to 92).
        api_key: Optional Open-Meteo API key, required for commercial use.

    Returns:
        pd.DataFrame: Weather forecast data from Open-Meteo that is as raw as possible.
    """
    _check_coordinates(latitude, longitude)
    _check_forecast_period(forecast_days, past_days)

    data = _request_open_meteo(
        url=FORECAST_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(HOURLY_VARIABLES_FORECAST),
            "forecast_days": forecast_days,
            "past_days": past_days,
            # request UTC and m/s to match the core data format
            "timezone": "GMT",
            "wind_speed_unit": "ms",
        },
        api_key=api_key,
    )

    return _hourly_to_dataframe(data)


def import_meta_open_meteo_historical(
    latitude: float, longitude: float, station_name: str = None, api_key: str = None
) -> MetaData:
    """
    Get the metadata of the Open-Meteo archive grid point closest to the given coordinates.

    Args:
        latitude: Latitude of the desired location in degree.
        longitude: Longitude of the desired location in degree.
        station_name: Optional name of the location, used for the file names of the exports.
        api_key: Optional Open-Meteo API key, required for commercial use.

    Returns:
        MetaData: An object of the MetaData class with populated attributes.
    """
    _check_coordinates(latitude, longitude)

    # the requested day is irrelevant for the metadata, use a day that always exists
    data = _request_open_meteo(
        url=ARCHIVE_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "start_date": ARCHIVE_FIRST_DAY.isoformat(),
            "end_date": ARCHIVE_FIRST_DAY.isoformat(),
            # let Open-Meteo resolve the local timezone of the location
            "timezone": "auto",
        },
        api_key=api_key,
    )

    return _response_to_meta(
        data, input_source="Open-Meteo Historical", station_name=station_name
    )


def import_meta_open_meteo_forecast(
    latitude: float, longitude: float, station_name: str = None, api_key: str = None
) -> MetaData:
    """
    Get the metadata of the Open-Meteo forecast grid point closest to the given coordinates.

    Args:
        latitude: Latitude of the desired location in degree.
        longitude: Longitude of the desired location in degree.
        station_name: Optional name of the location, used for the file names of the exports.
        api_key: Optional Open-Meteo API key, required for commercial use.

    Returns:
        MetaData: An object of the MetaData class with populated attributes.
    """
    _check_coordinates(latitude, longitude)

    data = _request_open_meteo(
        url=FORECAST_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "forecast_days": 1,
            # let Open-Meteo resolve the local timezone of the location
            "timezone": "auto",
        },
        api_key=api_key,
    )

    return _response_to_meta(
        data, input_source="Open-Meteo Forecast", station_name=station_name
    )


def _request_open_meteo(url: str, params: dict, api_key: str = None) -> dict:
    """
    Request data from Open-Meteo and return the json response as dictionary.

    Args:
        url: URL of the Open-Meteo endpoint.
        params: Parameters of the request.
        api_key: Optional Open-Meteo API key, required for commercial use.

    Returns:
        dict: The json response of Open-Meteo.
    """
    if api_key:
        url = CUSTOMER_URLS[url]
        params = {**params, "apikey": api_key}

    last_exception = None

    for attempt in range(_RETRIES):
        try:
            response = requests.get(url, params=params, timeout=_TIMEOUT)

            # retrying an exceeded rate limit would not help either
            if response.status_code == 429:
                raise ConnectionError(
                    f"The request limit of Open-Meteo is exceeded: "
                    f"{_error_reason(response)}. Wait until the limit is reset or "
                    f"use an api key (see https://open-meteo.com/en/pricing)."
                )

            # Open-Meteo describes invalid requests (e.g. unavailable time
            # periods) in the json body, retrying would not help
            if response.status_code == 400:
                # do not expose the api key in the error message
                requested = {k: v for k, v in params.items() if k != "apikey"}
                raise ValueError(
                    f"Open-Meteo rejected the request: "
                    f"{_error_reason(response)} (requested: {requested})"
                )

            response.raise_for_status()
            return response.json()
        except requests.RequestException as excep:
            last_exception = excep
            logger.debug(
                "Pulling data from Open-Meteo failed (try %s of %s): %s",
                attempt + 1, _RETRIES, excep
            )

    raise ConnectionError(
        f"Could not pull data from Open-Meteo ({url}) within {_RETRIES} tries. "
        f"Last error: {last_exception}"
    ) from last_exception


def _error_reason(response: requests.Response) -> str:
    """Extract the error description that Open-Meteo returns for invalid requests."""
    try:
        return response.json().get("reason", response.text)
    except requests.RequestException:
        return response.text


def _hourly_to_dataframe(data: dict) -> pd.DataFrame:
    """
    Convert the hourly values of an Open-Meteo response to a dataframe
    with a datetime index in UTC.

    Args:
        data: The json response of Open-Meteo as dictionary.

    Returns:
        pd.DataFrame: Dataframe with one column per pulled variable.
    """
    hourly = data.get("hourly", {})
    if not hourly:
        raise ValueError(
            f"Open-Meteo did not return any weather data for the request. "
            f"Response: {data}"
        )

    df = pd.DataFrame(hourly)
    # timestamps are in UTC as the data is requested with timezone=GMT
    df["time"] = pd.to_datetime(df["time"])
    df = df.set_index("time").sort_index()

    if df.isna().all().all():
        logger.warning(
            "Open-Meteo returned only missing values. The requested time period "
            "is likely not (yet) available for the requested location."
        )

    return df


def _response_to_meta(data: dict, input_source: str, station_name: str = None) -> MetaData:
    """
    Convert the location information of an Open-Meteo response to the MetaData class.

    Open-Meteo does not provide weather stations but grid points. Hence, the coordinates
    and the altitude of the grid point used by Open-Meteo are stored as metadata, which
    may slightly differ from the requested coordinates.

    Args:
        data: The json response of Open-Meteo as dictionary.
        input_source: Name of the data source to be stored in the metadata.
        station_name: Optional name of the location, used for the file names of the exports.

    Returns:
        MetaData: An object of the MetaData class with populated attributes.
    """
    meta = MetaData()
    meta.latitude = data["latitude"]
    meta.longitude = data["longitude"]
    meta.altitude = data["elevation"]
    # Open-Meteo has no station ids, identify the location by its grid point
    meta.station_id = f"lat{meta.latitude:.4f}_lon{meta.longitude:.4f}"
    meta.station_name = station_name if station_name else "OpenMeteo"
    meta.input_source = input_source
    meta.set_imported_timezone(
        _standard_utc_offset(
            timezone_name=data.get("timezone"),
            utc_offset_seconds=data.get("utc_offset_seconds", 0),
        )
    )

    return meta


def _standard_utc_offset(timezone_name: str, utc_offset_seconds: int) -> int:
    """
    Get the standard (non-daylight-saving) UTC offset in full hours of the location.

    The offset is only used to export the data in local time. Daylight saving time is
    excluded, as the weather data covers time periods with and without daylight saving.

    Args:
        timezone_name: Name of the timezone as returned by Open-Meteo, e.g. 'Europe/Berlin'.
        utc_offset_seconds: UTC offset in seconds as returned by Open-Meteo. Used as
            fallback if the timezone name can not be resolved.

    Returns:
        int: The UTC offset of the location in full hours.
    """
    offset_hours = utc_offset_seconds / 3600

    try:
        local_time = dt.datetime.now(ZoneInfo(timezone_name))
        # subtracting the daylight saving time results in the standard offset,
        # independent of the current season and hemisphere
        offset_hours = (
            local_time.utcoffset() - local_time.dst()
        ).total_seconds() / 3600
    except (ZoneInfoNotFoundError, ValueError, TypeError) as excep:
        logger.warning(
            "Could not resolve the timezone '%s' (%s). Using the UTC offset "
            "returned by Open-Meteo, which may include daylight saving time.",
            timezone_name, excep
        )

    if offset_hours != int(offset_hours):
        logger.warning(
            "The timezone of the requested location deviates by %s hours from UTC. "
            "As only full hours are supported, the exports use UTC%+d instead.",
            offset_hours, round(offset_hours)
        )

    return round(offset_hours)


def _check_coordinates(latitude: float, longitude: float):
    """Make sure the coordinates are given and within the valid range."""
    if latitude is None or longitude is None:
        raise ValueError(
            "Latitude and longitude are required to pull data from Open-Meteo."
        )
    if not -90 <= latitude <= 90:
        raise ValueError(f"The latitude {latitude} is outside -90 and 90 degree.")
    if not -180 <= longitude <= 180:
        raise ValueError(f"The longitude {longitude} is outside -180 and 180 degree.")


def _check_forecast_period(forecast_days: int, past_days: int):
    """Make sure the requested forecast period is supported by Open-Meteo."""
    if not 0 <= forecast_days <= MAX_FORECAST_DAYS:
        raise ValueError(
            f"Open-Meteo provides forecasts for up to {MAX_FORECAST_DAYS} days, "
            f"{forecast_days} days are requested."
        )
    if not 0 <= past_days <= MAX_PAST_DAYS:
        raise ValueError(
            f"The Open-Meteo forecast API provides up to {MAX_PAST_DAYS} past days, "
            f"{past_days} days are requested. Use the historical data instead."
        )
    if forecast_days == 0 and past_days == 0:
        raise ValueError(
            "Either forecast_days or past_days must be greater than zero."
        )


def _limit_archive_dates(start_date: dt.date, end_date: dt.date) -> tuple:
    """
    Limit the requested days to the period the Open-Meteo archive provides data for,
    as requests outside that period are rejected.

    Args:
        start_date: First day to be pulled.
        end_date: Last day to be pulled.

    Returns:
        tuple: The limited start and end day.
    """
    # the archive is based on reanalysis data and therefore never covers future days
    last_available_day = dt.datetime.now(dt.timezone.utc).date()

    if start_date < ARCHIVE_FIRST_DAY:
        logger.warning(
            "The Open-Meteo archive starts at %s, the requested start %s is ignored.",
            ARCHIVE_FIRST_DAY, start_date
        )
        start_date = ARCHIVE_FIRST_DAY
    if end_date > last_available_day:
        logger.warning(
            "The Open-Meteo archive provides data until %s, the requested end %s "
            "is ignored. Use the forecast data for more recent data.",
            last_available_day, end_date
        )
        end_date = last_available_day

    if end_date < start_date:
        raise ValueError(
            f"The requested time period is outside the period provided by the "
            f"Open-Meteo archive ({ARCHIVE_FIRST_DAY} to {last_available_day})."
        )

    return start_date, end_date
