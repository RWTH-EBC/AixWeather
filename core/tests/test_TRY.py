"""
includes unittests for different TRY datasets
"""

import os
import unittest

from project_class import ProjectClassTRY
from config.definitions import ROOT_DIR
from core.tests import utils_4_tests


class BaseTRY(unittest.TestCase):
    @classmethod
    def init_and_run_TRY(cls, name: str, path: str):
        cls.c = ProjectClassTRY(path=path)
        cls.folder_tests = os.path.join(
            ROOT_DIR, f"core/tests/test_files/regular_tests/TRY/test_{name}"
        )

        utils_4_tests.run_all_functions(cls.c)

        cls.start_formatted = cls.c.start.strftime("%Y%m%d")
        cls.end_formatted = cls.c.end.strftime("%Y%m%d")
        cls.station_id = "UnknownStationID"
        cls.city = "Aachen"

    @classmethod
    def tearDownClass(cls) -> None:
        utils_4_tests.delete_created_result_files()


class TestDWDTRY2015(BaseTRY, utils_4_tests.RegressionTestsClass):
    @classmethod
    def setUpClass(cls):
        cls.init_and_run_TRY(
            "TRY2015",
            os.path.join(
                ROOT_DIR,
                r"core/tests/test_files/regular_tests/TRY/"
                "test_TRY2015/input/TRY2015_507931060546_Jahr.dat",
            ),
        )


class TestDWDTRY2015Sommer(BaseTRY, utils_4_tests.RegressionTestsClass):
    @classmethod
    def setUpClass(cls):
        cls.init_and_run_TRY(
            "TRY2015_Sommer",
            os.path.join(
                ROOT_DIR,
                r"core/tests/test_files/regular_tests/TRY/"
                "test_TRY2015_Sommer/input/TRY2015_507931060546_Somm.dat",
            ),
        )


class TestDWDTRY2045(BaseTRY, utils_4_tests.RegressionTestsClass):
    @classmethod
    def setUpClass(cls):
        cls.init_and_run_TRY(
            "TRY2045",
            os.path.join(
                ROOT_DIR,
                r"core/tests/test_files/regular_tests/TRY/"
                "test_TRY2045/input/TRY2045_507931060546_Jahr.dat",
            ),
        )