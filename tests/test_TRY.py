"""
includes unittests for different TRY datasets
"""
# pylint: disable=all

import os
import time
import unittest
import random

from aixweather import definitions
from aixweather.project_class import ProjectClassTRY
from tests import utils_4_tests


class BaseTRY(unittest.TestCase):
    @classmethod
    def init_and_run_TRY(cls, name: str, path: str, export_in_utc: bool):
        # running the tests on the CI server with different python versions simultaneously causes,
        # connection timeouts to nominatim, which is used to get the coordinates of the station.
        # Therefore, we use a random timer to avoid this issue.
        time.sleep(random.uniform(0, 20))

        abs_result_folder_path = os.path.join(definitions.result_folder_path(), name)
        cls.c = ProjectClassTRY(
            path=path, abs_result_folder_path=abs_result_folder_path
        )
        cls.folder_tests = os.path.join(
            definitions.ROOT_DIR, f"tests/test_files/regular_tests/TRY/test_{name}"
        )

        utils_4_tests.run_all_functions(project_class_instance=cls.c, export_in_utc=export_in_utc)

        cls.start_formatted = cls.c.start.strftime("%Y%m%d")
        cls.end_formatted = cls.c.end.strftime("%Y%m%d")
        cls.station_id = "UnknownStationID"
        cls.city = "Aachen"
        cls.export_in_utc = export_in_utc

    @classmethod
    def tearDownClass(cls) -> None:
        utils_4_tests.delete_created_result_files(cls.c.abs_result_folder_path)


class TestDWDTRY2015(BaseTRY, utils_4_tests.RegressionTestsClass):
    @classmethod
    def setUpClass(cls):
        cls.init_and_run_TRY(
            name="TRY2015",
            path=os.path.join(
                definitions.ROOT_DIR,
                r"tests/test_files/regular_tests/TRY/"
                "test_TRY2015/input/TRY2015_507931060546_Jahr.dat",
            ),
            export_in_utc=True
        )


class TestDWDTRY2015Sommer(BaseTRY, utils_4_tests.RegressionTestsClass):
    @classmethod
    def setUpClass(cls):
        cls.init_and_run_TRY(
            name="TRY2015_Sommer",
            path=os.path.join(
                definitions.ROOT_DIR,
                r"tests/test_files/regular_tests/TRY/"
                "test_TRY2015_Sommer/input/TRY2015_507931060546_Somm.dat",
            ),
            export_in_utc=True
        )


class TestDWDTRY2045(BaseTRY, utils_4_tests.RegressionTestsClass):
    @classmethod
    def setUpClass(cls):
        cls.init_and_run_TRY(
            name="TRY2045",
            path=os.path.join(
                definitions.ROOT_DIR,
                r"tests/test_files/regular_tests/TRY/"
                "test_TRY2045/input/TRY2045_507931060546_Jahr.dat",
            ),
            export_in_utc=True
        )


class TestDWDTRY2015TimeZoneExport(BaseTRY, utils_4_tests.RegressionTestsClass):
    @classmethod
    def setUpClass(cls):
        cls.init_and_run_TRY(
            name="TRY2015",
            path=os.path.join(
                definitions.ROOT_DIR,
                r"tests/test_files/regular_tests/TRY/"
                "test_TRY2015/input/TRY2015_507931060546_Jahr.dat",
            ),
            export_in_utc=False
        )
