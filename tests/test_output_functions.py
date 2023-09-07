"""
includes untittests for output functions
"""

import os.path
import datetime as dt
import unittest
import json

import pandas as pd

from tests import utils_4_tests
from config.definitions import ROOT_DIR
from aixweather.imports.utils_import import MetaData
from aixweather.project_class import ProjectClassDWDHistorical
from aixweather.core_data_format_2_output_file import utils_2output


class BaseOutputFunction(unittest.TestCase):
    def init(cls, name: str, start: dt.datetime, end: dt.datetime, station=15000):
        cls.c = ProjectClassDWDHistorical(start=start, end=end, station=station)
        cls.folder_tests = os.path.join(
            ROOT_DIR,
            f"tests/test_files/regular_tests/output_functions/test_{name}",
        )
        cls.start_formatted = start.strftime("%Y%m%d")
        cls.end_formatted = end.strftime("%Y%m%d")

        cls.station_id = station
        cls.city = "Aachen-Orsbach"

    @classmethod
    def tearDownClass(cls) -> None:
        utils_4_tests.delete_created_result_files()


class TestOutputFunction(BaseOutputFunction, utils_4_tests.RegressionTestsClass):
    """
    Attention at some day this pull will move from recent folder
    to historic folder, update desired outcome with new dates
    """

    @classmethod
    def setUpClass(cls):
        cls.init(
            cls,
            "output_function_via_DWDHist",
            dt.datetime(2022, 1, 1),
            dt.datetime(2023, 1, 1),
        )

        # import "core data" and "meta_data"
        input_file = os.path.join(
            cls.folder_tests, "input", "Station_Aachen-Orsbach_core_data.csv"
        )
        input_file_meta = os.path.join(
            cls.folder_tests, "input", "Station_Aachen-Orsbach_meta_data.json"
        )
        cls.c.core_data = pd.read_csv(input_file, index_col=0, parse_dates=True)
        with open(input_file_meta, "r") as meta_file:
            meta_json = json.load(meta_file)
        cls.c.meta_data = MetaData(**meta_json)


        cls.c.core_2_pickle()
        cls.c.core_2_json()
        cls.c.core_2_mos()
        cls.c.core_2_epw()
        cls.c.core_2_csv()

    # ignore core_data and meta_data tests
    def test_core_data(self):
        pass

    def test_meta_data(self):
        pass
