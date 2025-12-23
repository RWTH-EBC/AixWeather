"""
This script tests the impact of changes on the simulation with the TMYReader in AixLib.
"""
import logging
from pathlib import Path
import shutil

import pytest
import unittest
import sys
from aixweather import definitions


def get_mos_files_to_simulate():
    mos_files = []
    for folder, subdir, files in os.walk(definitions.ROOT_DIR.joinpath("tests", "test_files")):
        for file in files:
            if file.endswith(".mos"):
                mos_files.append(Path(folder).joinpath(file))
    return mos_files


@pytest.mark.dymola
class TestAnotherDymolaFeature(unittest.TestCase):

    def setUp(self):
        self.simulation_dir = Path(__file__).parent.joinpath("tmp_simulation")
        self.model_name = "TestTiltedSurfaces"
        self.reference_path = Path(__file__).parent.joinpath("test_files", "simulation_results")

    def start_dymola(self):
        from ebcpy import DymolaAPI
        if "linux" in sys.platform:
            dymola_exe_path = "/usr/local/bin/dymola"
        else:
            dymola_exe_path = None
        
        package_path = Path(__file__).parent.joinpath("test_files", "modelica", "TestTiltedSurfaces.mo")
        aixlib_dir = self.simulation_dir.joinpath("tmp_AixLib")
        subprocess.run(
            ["git", "clone", "https://github.com/RWTH-EBC/AixLib", str(aixlib_dir)],
            check=True
        )
        path_aixlib = aixlib_dir.joinpath("AixLib/package.mo")
        return DymolaAPI(
            working_directory=self.example_sim_dir,
            model_name=model_name,
            packages=[
                package_path,
                aixlib_dir
            ],
            dymola_exe_path=dymola_exe_path,
            n_cpu=1,
        )

    def create_results(self):
        mos_files = get_mos_files_to_simulate()
        dym_api = self.start_dymola()
        self.simulate_mos_files(
            dym_api=dym_api,
            mos_files=mos_files,
            savepath=self.reference_path
        )

    def simulate_mos_files(self, dym_api, mos_files, savepath):
        model_names = []
        result_names = []
        for mos_file in mos_files:
            model_names.append(f'TestTiltedSurfaces(filNam=Modelica.Utilities.Files.loadResource("{file.as_posix()}")')
            result_names.append(mos_file.stem)

        result_file_names = dym_api.simulate(
            model_names=model_names,
            result_file_name=result_names,
            savepath=savepath
        )
        return dict(zip(mos_files, result_file_names))

    def tearDown(self):
            try:
                shutil.rmtree(self.simulation_dir)
            except (FileNotFoundError, PermissionError):
                logging.error("Could not delete temporary simulation directory!")
