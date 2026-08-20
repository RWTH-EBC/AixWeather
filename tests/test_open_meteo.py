"""
includes unittests for Open-Meteo data
"""
# pylint: disable=all

import datetime as dt
import json
import os.path
import unittest

import pandas as pd
from parameterized import parameterized, parameterized_class

from aixweather import definitions
from aixweather.imports.open_meteo import (
    HOURLY_VARIABLES_FORECAST,
    HOURLY_VARIABLES_HISTORICAL,
    _response_to_meta,
    _standard_utc_offset,
    import_meta_open_meteo_forecast,
    import_open_meteo_forecast,
    import_open_meteo_historical,
)
from aixweather.imports.utils_import import MetaData
from aixweather.project_class import (
    ProjectClassOpenMeteoForecast,
    ProjectClassOpenMeteoHistorical,
)
from aixweather.transformation_to_core_data.open_meteo import (
    OpenMeteoForecastFormat,
    OpenMeteoHistoricalFormat,
)
from tests import utils_4_tests


LATITUDE = 50.7893  # Aachen
LONGITUDE = 6.0516
STATION_NAME = "Aachen"


class TestOpenMeteoFormat(unittest.TestCase):
    """
    The pulled variables and the format dictionaries, which describe how to transform
    them, must always match.
    """

    @parameterized.expand(
        [
            (
                "historical",
                HOURLY_VARIABLES_HISTORICAL,
                OpenMeteoHistoricalFormat.import_format(),
            ),
            (
                "forecast",
                HOURLY_VARIABLES_FORECAST,
                OpenMeteoForecastFormat.import_format(),
            ),
        ]
    )
    def test_pulled_variables_match_format(self, name, pulled_variables, format_dict):
        self.assertListEqual(sorted(pulled_variables), sorted(format_dict.keys()))


class TestOpenMeteoInvalidRequests(unittest.TestCase):
    """Invalid requests must be rejected before pulling data."""

    def test_invalid_coordinates(self):
        with self.assertRaises(ValueError):
            import_meta_open_meteo_forecast(latitude=100, longitude=LONGITUDE)
        with self.assertRaises(ValueError):
            import_meta_open_meteo_forecast(latitude=LATITUDE, longitude=200)

    def test_invalid_forecast_period(self):
        with self.assertRaises(ValueError):
            import_open_meteo_forecast(
                latitude=LATITUDE, longitude=LONGITUDE, forecast_days=20
            )
        with self.assertRaises(ValueError):
            import_open_meteo_forecast(
                latitude=LATITUDE, longitude=LONGITUDE, past_days=100
            )

    def test_period_outside_archive(self):
        with self.assertRaises(ValueError):
            import_open_meteo_historical(
                start=dt.datetime.now() + dt.timedelta(days=10),
                end=dt.datetime.now() + dt.timedelta(days=20),
                latitude=LATITUDE,
                longitude=LONGITUDE,
            )


class TestOpenMeteoMetaData(unittest.TestCase):
    """Test the conversion of the location information to the metadata."""

    # response of Open-Meteo without weather data
    response = {
        "latitude": 50.79086,
        "longitude": 6.085409,
        "elevation": 200.0,
        "utc_offset_seconds": 7200,
        "timezone": "Europe/Berlin",
        "timezone_abbreviation": "GMT+2",
    }

    def test_response_to_meta(self):
        meta = _response_to_meta(
            self.response, input_source="Open-Meteo Historical", station_name="Aachen"
        )
        self.assertEqual(meta.station_name, "Aachen")
        # the station id is used for file names, hence no dots
        self.assertEqual(meta.station_id, "lat50-7909_lon6-0854")
        self.assertEqual(meta.latitude, 50.79086)
        self.assertEqual(meta.longitude, 6.08541)
        self.assertEqual(meta.altitude, 200.0)
        self.assertEqual(meta.input_source, "Open-Meteo Historical")
        # daylight saving time must not be used for the export
        self.assertEqual(meta.timezone, 1)

    def test_response_to_meta_without_station_name(self):
        meta = _response_to_meta(self.response, input_source="Open-Meteo Forecast")
        self.assertEqual(meta.station_name, "OpenMeteo")

    def test_standard_utc_offset(self):
        # daylight saving time must be excluded, also on the southern hemisphere
        self.assertEqual(_standard_utc_offset("Europe/Berlin", 7200), 1)
        self.assertEqual(_standard_utc_offset("Australia/Sydney", 39600), 10)
        # timezones with fractions of hours are rounded, as the export only
        # supports full hours
        self.assertEqual(_standard_utc_offset("Asia/Kathmandu", 20700), 6)

    def test_standard_utc_offset_of_unknown_timezone(self):
        # fall back to the offset given by Open-Meteo
        self.assertEqual(_standard_utc_offset("Not/ATimezone", 7200), 2)


class BaseOpenMeteo(unittest.TestCase):
    @classmethod
    def load_imported_data(cls, imported_data_file: str, meta_data_file: str):
        """Load the imported data and meta data of a previous pull to test the
        transformations without pulling data."""
        cls.c.imported_data = pd.read_csv(
            os.path.join(cls.folder_tests, "input", imported_data_file),
            index_col=0,
            parse_dates=True,
        )
        with open(
            os.path.join(cls.folder_tests, "input", meta_data_file), "r"
        ) as meta_file:
            cls.c.meta_data = MetaData(**json.load(meta_file))

    @classmethod
    def transform_and_export(cls, export_in_utc: bool):
        cls.c.data_2_core_data()
        cls.c.core_2_pickle()
        cls.c.core_2_json()
        cls.c.core_2_csv()
        cls.c.core_2_mos(export_in_utc=export_in_utc)
        cls.c.core_2_epw(export_in_utc=export_in_utc)

        cls.start_formatted = cls.c.start.strftime("%Y%m%d")
        cls.end_formatted = cls.c.end.strftime("%Y%m%d")
        cls.station_id = cls.c.meta_data.station_id
        cls.city = cls.c.meta_data.station_name

    @classmethod
    def tearDownClass(cls) -> None:
        utils_4_tests.delete_created_result_files(cls.c.abs_result_folder_path)


@parameterized_class([dict(export_in_utc=export_in_utc) for export_in_utc in [True, False]])
class TestOpenMeteoHistoricalFromImportedData(
    BaseOpenMeteo, utils_4_tests.RegressionTestsClass
):
    """Test the transformation of historical data with data of a previous pull."""

    export_in_utc = None

    @classmethod
    def setUpClass(cls):
        name = "historical_10days_Aachen"
        cls.c = ProjectClassOpenMeteoHistorical(
            start=dt.datetime(2023, 1, 1),
            end=dt.datetime(2023, 1, 10),
            latitude=LATITUDE,
            longitude=LONGITUDE,
            station_name=STATION_NAME,
            abs_result_folder_path=os.path.join(definitions.result_folder_path(), name),
        )
        cls.folder_tests = os.path.join(
            definitions.ROOT_DIR, f"tests/test_files/regular_tests/open_meteo/test_{name}"
        )

        cls.load_imported_data(
            imported_data_file="historical_imported_data_Aachen.csv",
            meta_data_file="Station_Aachen_meta_data.json",
        )
        cls.transform_and_export(export_in_utc=cls.export_in_utc)


@parameterized_class([dict(export_in_utc=export_in_utc) for export_in_utc in [True, False]])
class TestOpenMeteoForecastFromImportedData(
    BaseOpenMeteo, utils_4_tests.RegressionTestsClass, utils_4_tests.DatetimeIndexTestsClass
):
    """Test the transformation of forecast data with data of a previous pull."""

    export_in_utc = None

    @classmethod
    def setUpClass(cls):
        name = "forecast_august_2026_Aachen"
        cls.c = ProjectClassOpenMeteoForecast(
            latitude=LATITUDE,
            longitude=LONGITUDE,
            station_name=STATION_NAME,
            abs_result_folder_path=os.path.join(definitions.result_folder_path(), name),
        )
        cls.folder_tests = os.path.join(
            definitions.ROOT_DIR, f"tests/test_files/regular_tests/open_meteo/test_{name}"
        )

        cls.load_imported_data(
            imported_data_file="forecast_imported_data_Aachen.csv",
            meta_data_file="Station_Aachen_meta_data.json",
        )
        cls.transform_and_export(export_in_utc=cls.export_in_utc)


class TestOpenMeteoNoAssert(BaseOpenMeteo):
    """Pull data from Open-Meteo to test the imports without asserting the results."""

    @parameterized.expand(
        [
            (
                "historical_recent",
                dt.datetime.now() - dt.timedelta(days=10),
                dt.datetime.now() - dt.timedelta(days=3),
            ),
            (
                "historical_leapyear",
                dt.datetime(2020, 2, 25),
                dt.datetime(2020, 3, 5),
            ),
        ]
    )
    def test_historical_import_and_transformation_without_assert(self, name, start, end):
        # enable teardown clean up through the same result folder per parameter set
        name = "TestOpenMeteoNoAssert"
        self.__class__.c = ProjectClassOpenMeteoHistorical(
            start=start,
            end=end,
            latitude=LATITUDE,
            longitude=LONGITUDE,
            abs_result_folder_path=os.path.join(definitions.result_folder_path(), name),
        )
        utils_4_tests.run_all_functions(
            project_class_instance=self.c, export_in_utc=False
        )

    def test_forecast_import_and_transformation_without_assert(self):
        name = "TestOpenMeteoNoAssert"
        self.__class__.c = ProjectClassOpenMeteoForecast(
            latitude=LATITUDE,
            longitude=LONGITUDE,
            forecast_days=3,
            past_days=2,
            abs_result_folder_path=os.path.join(definitions.result_folder_path(), name),
        )
        utils_4_tests.run_all_functions(
            project_class_instance=self.c, export_in_utc=False
        )


def create_imported_data_for_unit_test():
    """
    in order to create new imported data if something changes.
    For manual use to create unit tests
    """

    c = ProjectClassOpenMeteoHistorical(
        start=dt.datetime(2023, 1, 1),
        end=dt.datetime(2023, 1, 10),
        latitude=LATITUDE,
        longitude=LONGITUDE,
        station_name=STATION_NAME,
    )
    c.import_data()
    c.imported_data.to_csv(
        definitions.results_file_path("historical_imported_data_Aachen.csv"), index=True
    )

    f = ProjectClassOpenMeteoForecast(
        latitude=LATITUDE,
        longitude=LONGITUDE,
        station_name=STATION_NAME,
    )
    f.import_data()
    f.imported_data.to_csv(
        definitions.results_file_path("forecast_imported_data_Aachen.csv"), index=True
    )
