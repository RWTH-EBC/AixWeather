"""
includes unittests for different TRY datasets
"""

import os
import unittest

from aixweather import definitions
from aixweather.project_class import ProjectClassTRY
from tests import utils_4_tests


class BaseTRY(unittest.TestCase):
    @classmethod
    def init_and_run_TRY(cls, name: str, path: str):
        abs_result_folder_path = os.path.join(definitions.result_folder_path(), name)
        cls.c = ProjectClassTRY(
            path=path, abs_result_folder_path=abs_result_folder_path
        )
        cls.folder_tests = os.path.join(
            definitions.ROOT_DIR, f"tests/test_files/regular_tests/TRY/test_{name}"
        )

        utils_4_tests.run_all_functions(cls.c)

        cls.start_formatted = cls.c.start.strftime("%Y%m%d")
        cls.end_formatted = cls.c.end.strftime("%Y%m%d")
        cls.station_id = "UnknownStationID"
        cls.city = "Aachen"

    @classmethod
    def tearDownClass(cls) -> None:
        utils_4_tests.delete_created_result_files(cls.c.abs_result_folder_path)


class TestDWDTRY2015(BaseTRY, utils_4_tests.RegressionTestsClass):
    @classmethod
    def setUpClass(cls):
        cls.init_and_run_TRY(
            "TRY2015",
            os.path.join(
                definitions.ROOT_DIR,
                r"tests/test_files/regular_tests/TRY/"
                "test_TRY2015/input/TRY2015_507931060546_Jahr.dat",
            ),
        )


class TestDWDTRY2015Sommer(BaseTRY, utils_4_tests.RegressionTestsClass):
    @classmethod
    def setUpClass(cls):
        cls.init_and_run_TRY(
            "TRY2015_Sommer",
            os.path.join(
                definitions.ROOT_DIR,
                r"tests/test_files/regular_tests/TRY/"
                "test_TRY2015_Sommer/input/TRY2015_507931060546_Somm.dat",
            ),
        )


class TestDWDTRY2045(BaseTRY, utils_4_tests.RegressionTestsClass):
    @classmethod
    def setUpClass(cls):
        cls.init_and_run_TRY(
            "TRY2045",
            os.path.join(
                definitions.ROOT_DIR,
                r"tests/test_files/regular_tests/TRY/"
                "test_TRY2045/input/TRY2045_507931060546_Jahr.dat",
            ),
        )
