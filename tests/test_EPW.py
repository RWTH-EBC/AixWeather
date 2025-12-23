"""
includes unittests for EPW data
"""
import itertools
# pylint: disable=all

import os
import unittest

from aixweather import definitions
from aixweather.project_class import ProjectClassEPW
from tests import utils_4_tests
from parameterized import parameterized_class


class BaseEPW(unittest.TestCase):
    @classmethod
    def init_and_run_EPW(cls, name: str, path: str, export_in_utc: bool):
        abs_result_folder_path = os.path.join(definitions.result_folder_path(), name)
        cls.c = ProjectClassEPW(
            path=path, abs_result_folder_path=abs_result_folder_path
        )
        cls.folder_tests = os.path.join(
            definitions.ROOT_DIR, f"tests/test_files/regular_tests/EPW/test_{name}"
        )

        utils_4_tests.run_all_functions(project_class_instance=cls.c, export_in_utc=export_in_utc)

        cls.start_formatted = cls.c.start.strftime("%Y%m%d")
        cls.end_formatted = cls.c.end.strftime("%Y%m%d")
        cls.station_id = "UnknownStationID"

    @classmethod
    def tearDownClass(cls) -> None:
        utils_4_tests.delete_created_result_files(cls.c.abs_result_folder_path)


NAMES_PATHS = [
    ("Essen", "EPW_Essen_Ladybug", "test_EPW_Essen_Ladybug/input/DEU_NW_Essen_104100_TRY2035_05_Wint_BBSR.epw"),
    ("Aachen", "EPW_Aachen_TMY", "test_EPW_Aachen_TMY/input/DEU_NW_Aachen.105010_TMYx.epw"),
    # A TMY file contains data from different years, but the data is selected to represent typical
    # conditions. Each month is from a different year, so the year is not continuous. This required
    # a special treatment, which correct behavior is tested here.
]

COMBINATIONS = [
    dict(
        city_input=city_name_path[0], path=city_name_path[2], export_in_utc=export_in_utc, name=city_name_path[1]
    ) for city_name_path, export_in_utc in itertools.product(NAMES_PATHS, [True, False])
]


@parameterized_class(COMBINATIONS)
class TestEPW(BaseEPW, utils_4_tests.RegressionTestsClass):

    city_input = None
    name = None
    export_in_utc = None
    path = None

    @classmethod
    def setUpClass(cls):
        if cls.path is None:
            raise unittest.SkipTest("Skipping base class TestEPW")

        cls.city = cls.city_input
        cls.init_and_run_EPW(
            cls.name,
            os.path.join(definitions.ROOT_DIR, "tests", "test_files", "regular_tests", "EPW", cls.path),
            export_in_utc=cls.export_in_utc
        )
