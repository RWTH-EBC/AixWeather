"""
includes unittests for EPW data
"""

import os
import unittest

from project_class import ProjectClassEPW
from config.definitions import ROOT_DIR
from tests import utils_4_tests


class BaseEPW(unittest.TestCase):
    @classmethod
    def init_and_run_EPW(cls, name: str, path: str):
        cls.c = ProjectClassEPW(path=path)
        cls.folder_tests = os.path.join(
            ROOT_DIR, f"tests/test_files/regular_tests/EPW/test_{name}"
        )

        utils_4_tests.run_all_functions(cls.c)

        cls.start_formatted = cls.c.start.strftime("%Y%m%d")
        cls.end_formatted = cls.c.end.strftime("%Y%m%d")
        cls.station_id = "UnknownStationID"
        cls.city = "Essen"

    @classmethod
    def tearDownClass(cls) -> None:
        utils_4_tests.delete_created_result_files()


class TestEPWEssenLadybug(BaseEPW, utils_4_tests.RegressionTestsClass):
    @classmethod
    def setUpClass(cls):
        cls.init_and_run_EPW(
            "EPW_Essen_Ladybug",
            os.path.join(
                ROOT_DIR,
                r"tests/test_files/regular_tests/EPW/test_EPW_Essen_Ladybug/"
                "input/DEU_NW_Essen_104100_TRY2035_05_Wint_BBSR.epw",
            ),
        )