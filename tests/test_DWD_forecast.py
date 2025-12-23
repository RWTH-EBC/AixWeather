"""
includes unittests for DWD forecast data
"""
# pylint: disable=all

import json
import os.path
import unittest
import pandas as pd

from parameterized import parameterized, parameterized_class

from aixweather import definitions
from aixweather.project_class import ProjectClassDWDForecast
from aixweather.imports.utils_import import MetaData
import utils_4_tests


class BaseDWDForecast(unittest.TestCase):
    @classmethod
    def init_and_run_DWD_forecast(cls, name: str, station: str, export_in_utc: bool):
        abs_result_folder_path = os.path.join(definitions.result_folder_path(), name)
        cls.c = ProjectClassDWDForecast(
            station=station, abs_result_folder_path=abs_result_folder_path
        )
        cls.folder_tests = os.path.join(
            definitions.ROOT_DIR, f"tests/test_files/regular_tests/DWD_forecast/test_{name}"
        )

        utils_4_tests.run_all_functions(project_class_instance=cls.c, export_in_utc=export_in_utc)

        cls.start_formatted = cls.c.start.strftime("%Y%m%d")
        cls.end_formatted = cls.c.end.strftime("%Y%m%d")
        cls.station_id = station
        cls.city = cls.c.meta_data.station_name

    @classmethod
    def tearDownClass(cls) -> None:
        utils_4_tests.delete_created_result_files(cls.c.abs_result_folder_path)


@parameterized_class([dict(export_in_utc=export_in_utc) for export_in_utc in [True, False]])
class TestDWDForecastFromImportedData(
    BaseDWDForecast, utils_4_tests.RegressionTestsClass
):

    export_in_utc = None

    @classmethod
    def setUpClass(cls):
        station = "06710"
        name = "06710_august_2023"
        abs_result_folder_path = os.path.join(definitions.result_folder_path(), name)
        cls.c = ProjectClassDWDForecast(
            station=station, abs_result_folder_path=abs_result_folder_path
        )
        cls.folder_tests = os.path.join(
            definitions.ROOT_DIR, f"tests/test_files/regular_tests/DWD_forecast/test_{name}"
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
        cls.c.core_2_mos(export_in_utc=cls.export_in_utc)
        cls.c.core_2_epw(export_in_utc=cls.export_in_utc)
        cls.c.core_2_csv()

        cls.start_formatted = cls.c.start.strftime("%Y%m%d")
        cls.end_formatted = cls.c.end.strftime("%Y%m%d")
        cls.station_id = station
        cls.city = cls.c.meta_data.station_name


class TestDWDForecastNoAssert(BaseDWDForecast):
    @parameterized.expand(
        [
            ("06710_forecast", "06710", True),
            ("06710_forecast", "06710", False),
        ]
    )
    def test_imports_and_transformation_without_assert(self, name, station, export_in_utc):
        self.init_and_run_DWD_forecast(name, station, export_in_utc)


def create_imported_data_for_unit_test():
    """
    in order to create new imported data if something changes.
    For manual use to create unit tests
    """

    c = ProjectClassDWDForecast(station="06710")
    c.import_data()
    c.imported_data.to_csv(
        definitions.results_file_path("forecast_imported_data_06710.csv"), index=True
    )
