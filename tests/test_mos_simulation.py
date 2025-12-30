"""
This script tests the impact of changes on the simulation with the TMYReader in AixLib.
"""
import logging
import os.path
from pathlib import Path
import shutil
import subprocess

import matplotlib.pyplot as plt
import pandas as pd
from pandas import testing as pd_testing
import pytest
import unittest
from unittest.mock import patch
import sys
from aixweather import definitions
from aixweather.project_class import ProjectClassTRY


def create_mos_files_to_simulate(result_folder):
    path = Path(definitions.ROOT_DIR).joinpath(
        "tests", "test_files", "regular_tests",
        "TRY", "test_TRY2015", "input", "TRY2015_507931060546_Jahr.dat"
    )
    project_class_instance = ProjectClassTRY(
        path=str(path), abs_result_folder_path=result_folder
    )
    mos_files = []
    with patch("aixweather.imports.TRY.get_city_from_location") as mock_get_city:
        mock_get_city.return_value = "Aachen"
        project_class_instance.import_data()
        project_class_instance.data_2_core_data()
        for timezone in range(-12, 13, 2):
            project_class_instance.meta_data.timezone = timezone
            project_class_instance.abs_result_folder_path = result_folder.joinpath(f"utc_{timezone}")
            mos_files.append(project_class_instance.core_2_mos(export_in_utc=False))
        project_class_instance.abs_result_folder_path = result_folder.joinpath(f"utc_export")
        mos_files.append(project_class_instance.core_2_mos(export_in_utc=True))
    return [Path(file) for file in mos_files]


def simulate_mos_files(dym_api, mos_files, savepath):
    model_names = []
    result_names = []
    savepath.mkdir(exist_ok=True)
    for mos_file in mos_files:
        model_names.append(
            f'TestTiltedSurfaces(filNam=Modelica.Utilities.Files.loadResource("{mos_file.as_posix()}"))'
        )
        result_names.append(savepath.joinpath(
            mos_file.parent.stem + "_" + mos_file.stem + ".csv"
        ))

    results = dym_api.simulate(
        return_option="time_series",
        model_names=model_names
    )
    for tsd, file in zip(results, result_names):
        relevant_cols = [
            col for col in tsd.columns
            if col.startswith("H") and "." not in col and col.endswith("]")
        ]
        tsd.loc[:, relevant_cols].to_csv(file, sep=";")
    return dict(zip(mos_files, result_names))


def start_dymola(simulation_dir):
    from ebcpy import DymolaAPI
    if "linux" in sys.platform:
        dymola_exe_path = "/usr/local/bin/dymola"
    else:
        dymola_exe_path = None

    package_path = Path(__file__).parent.joinpath("test_files", "modelica", "TestTiltedSurfaces.mo")
    aixlib_dir = simulation_dir.joinpath("tmp_AixLib")
    path_aixlib = aixlib_dir.joinpath("AixLib/package.mo")
    if not os.path.exists(path_aixlib):
        subprocess.run(
            ["git", "clone", "https://github.com/RWTH-EBC/AixLib", str(aixlib_dir)],
            check=True
        )
    dym_api = DymolaAPI(
        working_directory=simulation_dir,
        model_name=None,
        packages=[
            package_path,
            path_aixlib
        ],
        dymola_exe_path=dymola_exe_path,
        n_cpu=1,
    )
    dym_api.set_sim_setup({"start_time": 0, "stop_time": 86400, "output_interval": 3600})
    return dym_api


def create_results(simulation_dir, result_dir, create_plot: bool = False, summer: bool = False):
    mos_files = create_mos_files_to_simulate(result_folder=simulation_dir)
    dym_api = start_dymola(simulation_dir=simulation_dir)
    if summer:
        dym_api.set_sim_setup({"start_time": 86400 * 150, "stop_time": 86400 * 151, "output_interval": 3600})
    else:
        dym_api.set_sim_setup({"start_time": 0, "stop_time": 86400, "output_interval": 3600})
    results = simulate_mos_files(
        dym_api=dym_api,
        mos_files=mos_files,
        savepath=result_dir
    )
    if not create_plot:
        return results
    dfs = {}
    columns = None
    for mos_path, csv_path in results.items():
        df = pd.read_csv(csv_path, sep=";", index_col=0)
        columns = df.columns
        dfs[mos_path.parent.stem] = df
    columns = list(set([col.split("[")[0] for col in columns]))
    directions = {
        1: "South", 2: "West", 3: "North", 4: "East"
    }
    for col in columns:
        fig, axes = plt.subplots(4, 1, sharex=True)
        for i, ax in zip(range(1, 5), axes):
            for label, df in dfs.items():
                if label.startswith("utc_export"):
                    label = "utc"
                    linestyle = "--"
                else:
                    label = label.replace("utc_", "")
                    linestyle = "-"
                ax.plot(df.index / 3600, df.loc[:, f"{col}[{i}]"], label=label, linestyle=linestyle)
            ax.set_ylabel(directions[i])
        axes[0].legend(ncol=6)
        axes[-1].set_xlabel("Time in h")
        fig.tight_layout()
        fig.savefig(simulation_dir.joinpath(f"plots_summer={summer}_{col}.png"))


@pytest.mark.dymola
class TestTMY3MOSReaderImpactOfTimeZone(unittest.TestCase):

    def setUp(self):
        self.simulation_dir = Path(__file__).parent.joinpath("tmp_simulation")
        self.model_name = "TestTiltedSurfaces"
        self.reference_path = Path(__file__).parent.joinpath("test_files", "modelica")

    def test_reference_results_first_day(self):
        results = create_results(
            simulation_dir=self.simulation_dir,
            result_dir=self.simulation_dir.joinpath("results_first_day"),
            summer=False
        )
        self._compare_results(results, "first_day")

    def test_reference_results_summer(self):
        results = create_results(
            simulation_dir=self.simulation_dir,
            result_dir=self.simulation_dir.joinpath("results_summer"),
            summer=True
        )
        self._compare_results(results, "summer")

    def _compare_results(self, results, folder):
        failures = {}
        for file in results.values():
            df = pd.read_csv(file, sep=";", index_col=0)
            df_ref = pd.read_csv(self.reference_path.joinpath(folder, file.name), sep=";", index_col=0)
            try:
                pd_testing.assert_frame_equal(df, df_ref)
            except AssertionError as err:
                failures[file.name] = str(err)
        if failures:
            self.fail(
                f"{len(failures)} failed cases:\n" +
                f"\n\n".join([f'{name}:\n{msg}' for name, msg in failures.items()])
            )

    def tearDown(self):
        try:
            shutil.rmtree(self.simulation_dir)
        except (FileNotFoundError, PermissionError):
            logging.error("Could not delete temporary simulation directory!")


if __name__ == '__main__':
    create_results(
        simulation_dir=Path(r"D:\00_temp\tmp_aixweather"),
        result_dir=Path(definitions.ROOT_DIR).joinpath("tests", "test_files", "modelica", "summer"),
        create_plot=True,
        summer=True
    )
    create_results(
        simulation_dir=Path(r"D:\00_temp\tmp_aixweather"),
        result_dir=Path(definitions.ROOT_DIR).joinpath("tests", "test_files", "modelica", "first_day"),
        create_plot=True,
        summer=False
    )
