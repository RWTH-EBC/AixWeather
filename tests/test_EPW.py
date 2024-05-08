"""
includes unittests for EPW data
"""
# pylint: disable=all

import os
import unittest

from aixweather import definitions
from aixweather.project_class import ProjectClassEPW
from tests import utils_4_tests


class BaseEPW(unittest.TestCase):
    @classmethod
    def init_and_run_EPW(cls, name: str, path: str):
        abs_result_folder_path = os.path.join(definitions.result_folder_path(), name)
        cls.c = ProjectClassEPW(
            path=path, abs_result_folder_path=abs_result_folder_path
        )
        cls.folder_tests = os.path.join(
            definitions.ROOT_DIR, f"tests/test_files/regular_tests/EPW/test_{name}"
        )

        utils_4_tests.run_all_functions(cls.c)

        cls.start_formatted = cls.c.start.strftime("%Y%m%d")
        cls.end_formatted = cls.c.end.strftime("%Y%m%d")
        cls.station_id = "UnknownStationID"

    @classmethod
    def tearDownClass(cls) -> None:
        utils_4_tests.delete_created_result_files(cls.c.abs_result_folder_path)


class TestEPWEssenLadybug(BaseEPW, utils_4_tests.RegressionTestsClass):
    @classmethod
    def setUpClass(cls):
        cls.city = "Essen"
        cls.init_and_run_EPW(
            "EPW_Essen_Ladybug",
            os.path.join(
                definitions.ROOT_DIR,
                r"tests/test_files/regular_tests/EPW/test_EPW_Essen_Ladybug/"
                "input/DEU_NW_Essen_104100_TRY2035_05_Wint_BBSR.epw",
            ),
        )

class TestEPWAachenTMY(BaseEPW, utils_4_tests.RegressionTestsClass):
    """
    A TMY file contains data from different years, but the data is selected to represent typical
    conditions. Each month is from a different year, so the year is not continuous. This required
    a special treatment, which correct behavior is tested here.
    """
    @classmethod
    def setUpClass(cls):
        cls.city = "Aachen"
        cls.init_and_run_EPW(
            "EPW_Aachen_TMY",
            os.path.join(
                definitions.ROOT_DIR,
                r"tests/test_files/regular_tests/EPW/test_EPW_Aachen_TMY/"
                "input/DEU_NW_Aachen.105010_TMYx.epw",
            ),
        )

