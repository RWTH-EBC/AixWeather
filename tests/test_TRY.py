"""
includes unittests for different TRY datasets
"""
import itertools
# pylint: disable=all

import os
import time
import unittest
from unittest.mock import patch
import random
from parameterized import parameterized_class

from aixweather import definitions
from aixweather.project_class import ProjectClassTRY
from tests import utils_4_tests


class BaseTRY(unittest.TestCase):
    @classmethod
    def init_and_run_TRY(cls, name: str, path: str, export_in_utc: bool, city: str):
        abs_result_folder_path = os.path.join(definitions.result_folder_path(), name)
        cls.c = ProjectClassTRY(
            path=path, abs_result_folder_path=abs_result_folder_path
        )
        cls.folder_tests = os.path.join(
            definitions.ROOT_DIR, f"tests/test_files/regular_tests/TRY/test_{name}"
        )
        # Mock the external API requests to Nominatim to avoid http request errors.
        with patch("aixweather.imports.TRY.get_city_from_location") as mock_get_city:
            mock_get_city.return_value = city
            utils_4_tests.run_all_functions(cls.c, export_in_utc=export_in_utc)

        cls.start_formatted = cls.c.start.strftime("%Y%m%d")
        cls.end_formatted = cls.c.end.strftime("%Y%m%d")
        cls.station_id = "UnknownStationID"
        cls.city = "Aachen"
        cls.export_in_utc = export_in_utc

    @classmethod
    def tearDownClass(cls) -> None:
        utils_4_tests.delete_created_result_files(cls.c.abs_result_folder_path)


NAMES_PATHS = [
    ("TRY2015", "test_TRY2015/input/TRY2015_507931060546_Jahr.dat"),
    ("TRY2015_Sommer", "test_TRY2015_Sommer/input/TRY2015_507931060546_Somm.dat"),
    ("TRY2045", "test_TRY2045/input/TRY2045_507931060546_Jahr.dat"),
]

COMBINATIONS = [
    dict(
        path=name_path[1], export_in_utc=export_in_utc, name=name_path[0]
    ) for name_path, export_in_utc in itertools.product(NAMES_PATHS, [True, False])
]


@parameterized_class(COMBINATIONS)
class TestDWDTRY(BaseTRY, utils_4_tests.RegressionTestsClass):

    path = None
    export_in_utc = None
    name = None

    @classmethod
    def setUpClass(cls):
        if cls.path is None:
            raise unittest.SkipTest("Skipping base class TestDWDTRY")

        cls.init_and_run_TRY(
            name=cls.name,
            path=os.path.join(definitions.ROOT_DIR, "tests", "test_files", "regular_tests", "TRY", cls.path),
            export_in_utc=cls.export_in_utc,
            city="Aachen"
        )
