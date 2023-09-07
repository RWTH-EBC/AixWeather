"""
includes unittests for ERC data
"""

import os.path
import unittest
import datetime as dt

from tests import utils_4_tests
from config.definitions import ROOT_DIR
from aixweather.project_class import ProjectClassERC
from aixweather.core_data_format_2_output_file import utils_2output

# username="xxxxx@eonerc.rwth-aachen.de"
# password="xxxxx"
# cred = (username, password)

@unittest.skip("Dont test ERC data as there are no credentials available for testing.")
class BaseERC(unittest.TestCase):
    @classmethod
    def init_and_run_ERC(
        cls, name: str, start: dt.datetime, end: dt.datetime, cred=None
    ):
        cls.c = ProjectClassERC(start=start, end=end, cred=cred)
        cls.folder_tests = os.path.join(
            ROOT_DIR, f"tests/test_files/regular_tests/ERC_hist/test_{name}"
        )
        cls.start_formatted = start.strftime("%Y%m%d")
        cls.end_formatted = end.strftime("%Y%m%d")

        utils_4_tests.run_all_functions(cls.c)

        cls.station_id = "ERC"
        cls.city = "Old_Experimental_Hall"

    @classmethod
    def tearDownClass(cls) -> None:
        utils_4_tests.delete_created_result_files()

@unittest.skip("Dont test ERC data as there are no credentials available for testing.")
class TestERC10Days(BaseERC):
    """
    Attention at some day this pull will move from recent folder
    to historic folder, update desired outcome with new dates
    """

    def test_without_assert(self):
        self.init_and_run_ERC(
            "ERC_10Days", dt.datetime(2022, 1, 1), dt.datetime(2022, 1, 10), None
        )
