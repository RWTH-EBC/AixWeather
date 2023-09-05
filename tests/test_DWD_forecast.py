'''
includes unittests for DWD forecast data
'''
import json
import os.path
import unittest
import pandas as pd

from parameterized import parameterized

from AixWeather.project_class import ProjectClassDWDForecast
from AixWeather.imports.utils_import import MetaData
from AixWeather.core_data_format_2_output_file import utils_2output
from config.definitions import ROOT_DIR
import utils_4_tests


class BaseDWDForecast(unittest.TestCase):
    @classmethod
    def init_and_run_DWD_forecast(cls, name: str, station):
        cls.c = ProjectClassDWDForecast(station=station)
        cls.folder_tests = os.path.join(
            ROOT_DIR, f"tests/test_files/regular_tests/DWD_forecast/test_{name}"
        )

        utils_4_tests.run_all_functions(cls.c)

        cls.start_formatted = cls.c.start.strftime("%Y%m%d")
        cls.end_formatted = cls.c.end.strftime("%Y%m%d")
        cls.station_id = station
        cls.city = cls.c.meta_data.station_name

    @classmethod
    def tearDownClass(cls) -> None:
        utils_4_tests.delete_created_result_files()


class TestDWDForecastFromImportedData(
    BaseDWDForecast, utils_4_tests.RegressionTestsClass
):
    @classmethod
    def setUpClass(cls):
        station = "06710"
        name = "06710_august_2023"
        cls.c = ProjectClassDWDForecast(station=station)
        cls.folder_tests = os.path.join(
            ROOT_DIR, f"tests/test_files/regular_tests/DWD_forecast/test_{name}"
        )

        # import "imported data" and "meta_data"
        input_file = os.path.join(
            cls.folder_tests, "input", "forecast_imported_data_06710.csv"
        )
        input_file_meta = os.path.join(
            cls.folder_tests, "input", "Station_LAUSANNE_meta_data.json"
        )
        cls.c.imported_data = pd.read_csv(input_file, index_col=0, parse_dates=True)
        with open(input_file_meta, "r") as meta_file:
            meta_json = json.load(meta_file)
        cls.c.meta_data = MetaData(**meta_json)

        cls.c.data_2_core_data()
        cls.c.core_2_pickle()
        cls.c.core_2_json()
        cls.c.core_2_mos()
        cls.c.core_2_epw()
        cls.c.core_2_csv()

        cls.start_formatted = cls.c.start.strftime("%Y%m%d")
        cls.end_formatted = cls.c.end.strftime("%Y%m%d")
        cls.station_id = station
        cls.city = cls.c.meta_data.station_name


class TestDWDForecastNoAssert(BaseDWDForecast):
    @parameterized.expand(
        [
            (
                "06710_forecast",
                "06710",
            ),
        ]
    )
    def test_imports_and_transformation_without_assert(
            self, name, station
    ):
        self.init_and_run_DWD_forecast(name, station)


def create_imported_data_for_unit_test():
    """
    in order to create new imported data if something changes.
    For manual use to create unit tests
    """

    c = ProjectClassDWDForecast(station="06710")
    c.import_data()
    c.imported_data.to_csv(
        utils_2output.results_file_path("forecast_imported_data_06710.csv"), index=True
    )
