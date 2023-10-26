"""
includes unittests for DWD historical data
"""
# pylint: disable=all

import os.path
import unittest
import datetime as dt

from parameterized import parameterized

from aixweather import definitions
from aixweather.project_class import ProjectClassDWDHistorical
from tests import utils_4_tests


class BaseDWDHistorical(unittest.TestCase):
    @classmethod
    def init_and_run_DWD_historical(
        cls, name: str, start: dt.datetime, end: dt.datetime, station=15000
    ):
        abs_result_folder_path = os.path.join(definitions.result_folder_path(), name)
        cls.c = ProjectClassDWDHistorical(
            start=start,
            end=end,
            station=station,
            abs_result_folder_path=abs_result_folder_path,
        )
        cls.folder_tests = os.path.join(
            definitions.ROOT_DIR, f"tests/test_files/regular_tests/DWD_hist/test_{name}"
        )
        cls.start_formatted = start.strftime("%Y%m%d")
        cls.end_formatted = end.strftime("%Y%m%d")

        utils_4_tests.run_all_functions(cls.c)

        cls.station_id = station
        cls.city = "Aachen-Orsbach"

    @classmethod
    def tearDownClass(cls) -> None:
        utils_4_tests.delete_created_result_files(cls.c.abs_result_folder_path)


class TestDWDHistorical1Year(BaseDWDHistorical, utils_4_tests.RegressionTestsClass):
    """
    Attention at some day this pull will move from recent folder
    to historic folder, update desired outcome with new dates
    """

    @classmethod
    def setUpClass(cls):
        cls.init_and_run_DWD_historical(
            "historical_1year", dt.datetime(2022, 1, 1), dt.datetime(2023, 1, 1)
        )


class TestDWDHistorical10Days(BaseDWDHistorical, utils_4_tests.RegressionTestsClass):
    """
    Attention at some day this pull will move from recent folder
    to historic folder, update desired outcome with new dates
    """

    @classmethod
    def setUpClass(cls):
        cls.init_and_run_DWD_historical(
            "historical_10days", dt.datetime(2022, 1, 1), dt.datetime(2022, 1, 10)
        )


class TestDWDHistoricalNoAssert(BaseDWDHistorical):
    @parameterized.expand(
        [
            (
                "pull_recent_folder",
                dt.datetime.now() - dt.timedelta(days=10),
                dt.datetime.now() - dt.timedelta(days=3),
            ),
            (
                "pull_from_historicalfolder",
                dt.datetime(2020, 5, 2),
                dt.datetime(2023, 5, 3),
            ),
            (
                "historical_1leapyear",
                dt.datetime(2020, 1, 1),
                dt.datetime(2021, 1, 1),
            ),  # Todo: check how programs (e.g. TMY3Reader or EnergyPlus) handle leap year data and apply handling here respectively
            (
                "from_recent_folder_and_historical_folder",
                dt.datetime.now() - dt.timedelta(days=600),
                dt.datetime.now() - dt.timedelta(days=3),
            ),
        ]
    )
    def test_imports_and_transformation_without_assert(self, name, start, end):
        name = "TestDWDHistoricalNoAssert" # enable teardown clean up through same result folder per parameter set
        self.init_and_run_DWD_historical(name, start, end)
