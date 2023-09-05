"""
This module contains functions and classes for testing. It provides utilities
to load data, compare results and execute tests
"""

import re
import json
import shutil
import os.path
import pandas as pd

from AixWeather.core_data_format_2_output_file import utils_2output
from AixWeather.imports.utils_import import MetaData


def load_mos(folder_tests, file_name):
    with open(os.path.join(folder_tests, file_name), "r") as file:
        mos_desired = file.read()
    with open(utils_2output.results_file_path(file_name), "r") as file:
        mos_created = file.read()
    # delete time of data pull
    pattern = r"\(collected at \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}\)"
    mos_desired = re.sub(pattern, "", mos_desired)
    mos_created = re.sub(pattern, "", mos_created)
    return mos_desired, mos_created


def load_epw(folder_tests, file_name):
    with open(os.path.join(folder_tests, file_name), "r") as file:
        epw_desired = file.read()
    with open(utils_2output.results_file_path(file_name), "r") as file:
        epw_created = file.read()
    return epw_desired, epw_created


def load_json(folder_tests, file_name):
    with open(os.path.join(folder_tests, file_name), "r") as file:
        json_desired = json.load(file)
    with open(utils_2output.results_file_path(file_name), "r") as file:
        json_created = json.load(file)
    return json_desired, json_created


def load_csv(folder_tests, file_name):
    csv_desired = pd.read_csv(os.path.join(folder_tests, file_name))
    csv_created = pd.read_csv(utils_2output.results_file_path(file_name))
    return csv_desired, csv_created


def delete_created_result_files():
    # cleans results folder
    file_path = utils_2output.results_file_path("temp.txt")
    directory_path = os.path.dirname(file_path)
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)
        os.makedirs(directory_path)


def run_all_functions(project_class_instance):
    """
    This function runs a series of methods on a project class instance to import and process weather data. It is
    intended for testing and validation purposes.

    Args:
        project_class_instance: An instance of a project class inheriting from ProjectClassGeneral.
    """
    project_class_instance.import_data()
    project_class_instance.data_2_core_data()

    project_class_instance.core_2_pickle()
    project_class_instance.core_2_json()
    project_class_instance.core_2_csv()
    project_class_instance.core_2_mos()
    project_class_instance.core_2_epw()


class RegressionTestsClass:
    """
    A class containing regression tests for validating the output files of the project.

    This class defines a set of test methods to compare the project's output with desired reference data.

    Methods:
        test_core_data(): Test the core weather data against a reference pickle file.
        test_meta_data(): Test the project's metadata against a reference JSON file.
        test_output_json(): Test the project's JSON output against a reference JSON file.
        test_output_csv(): Test the project's CSV output against a reference CSV file.
        test_output_mos(): Test the project's MOS output against a reference MOS file.
        test_output_epw(): Test the project's EPW output against a reference EPW file.
    """

    def test_core_data(self):
        df_core_desired = pd.read_pickle(
            os.path.join(self.folder_tests, f"Station_{self.city}.pkl")
        )
        pd.testing.assert_frame_equal(df_core_desired, self.c.core_data)

    def test_meta_data(self):
        with open(
            os.path.join(self.folder_tests, f"Station_{self.city}_meta_data.json"), "r"
        ) as meta_file:
            meta_json = json.load(meta_file)
        meta_desired = MetaData(**meta_json)

        attributes_to_skip = {
            "executed_transformations",
            "executed_transformations_no_shift",
            "station_exists_until",
        }  # Define the attributes you want to skip

        attrs_desired = set(vars(meta_desired).keys()) - attributes_to_skip
        attrs_current = set(vars(self.c.meta_data).keys()) - attributes_to_skip

        # Check if both objects have the same set of attributes (excluding the ones to skip)
        self.assertSetEqual(attrs_desired, attrs_current)

        for attr in attrs_desired:
            self.assertEqual(
                meta_desired.__dict__[attr], self.c.meta_data.__dict__[attr]
            )

    def test_output_json(self):
        json_desired, json_created = load_json(
            self.folder_tests, f"Station_{self.city}.json"
        )
        json_desired = json.dumps(json_desired, sort_keys=True)
        json_created = json.dumps(json_created, sort_keys=True)
        # comparison of two jsons takes very long, serialize them first
        self.assertEqual(
            json_desired[:1000],
            json_created[:1000],
            "First 1000 characters don't match!",
        )
        self.assertEqual(
            json_desired[-1000:],
            json_created[-1000:],
            "Last 1000 characters don't match!",
        )
        self.assertEqual(json_desired, json_created)

    def test_output_csv(self):
        csv_desired, csv_created = load_csv(
            self.folder_tests, f"Station_{self.city}.csv"
        )
        pd.testing.assert_frame_equal(csv_desired, csv_created)

    def test_output_mos(self):
        mos_desired, mos_created = load_mos(
            self.folder_tests,
            f"{self.station_id}_{self.start_formatted}_{self.end_formatted}_{self.city}.mos",
        )
        self.assertEqual(
            mos_desired[:1000], mos_created[:1000], "First 1000 characters don't match!"
        )
        self.assertEqual(
            mos_desired[-1000:],
            mos_created[-1000:],
            "Last 1000 characters don't match!",
        )
        self.assertEqual(mos_desired, mos_created)

    # @unittest.skip("Temporaily skip, to see if other errors arise.")
    # def test_output_epw(self):
    #     epw_desired, epw_created = load_epw(
    #         self.folder_tests,
    #         f"{self.station_id}_{self.start_formatted}_{self.end_formatted}_{self.city}.epw",
    #     )
    #     self.maxDiff = None
    #     self.assertEqual(
    #         epw_desired[:1000], epw_created[:1000], "First 1000 characters don't match!"
    #     )
    #     self.assertEqual(
    #         epw_desired[-1000:],
    #         epw_created[-1000:],
    #         "Last 1000 characters don't match!",
    #     )
    #     self.assertEqual(epw_desired, epw_created)


class DatetimeIndexTestsClass:
    def test_is_continuous_datetime_index(self):
        # Calculate differences between adjacent dates
        date_diffs = self.c.core_data.index.to_series().diff().dropna()

        # Check if the difference is consistent
        self.assertTrue(date_diffs.nunique() == 1)
