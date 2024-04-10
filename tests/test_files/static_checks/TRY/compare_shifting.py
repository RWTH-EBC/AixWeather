"""
Includes a class for unit tests for TRY data
"""

import os
import unittest
import pandas as pd

from aixweather.project_class import ProjectClassTRY
from aixweather import definitions


class TestDWDTRY(unittest.TestCase):
    def load_files(self):
        self.old_conv = pd.read_table(
            filepath_or_buffer=rf"{definitions.ROOT_DIR}/tests/test_files/static_checks/"
                               "TRY/TRY2015_507931060546_Jahr_City_Aachen"
                               "_oldConverter.mos",
            header=40,
            sep='\s+',
            skip_blank_lines=False,
            encoding="latin",
        )

        self.new_conv_no_shifting = pd.read_table(
            filepath_or_buffer=rf"{definitions.ROOT_DIR}/tests/test_files/static_checks/"
                               "TRY/UnknownStationID_20150101_20160101_Aachen"
                               "_without_time_shifting.mos",
            header=43,
            sep='\s+',
            skip_blank_lines=False,
            encoding="latin",
        )

        self.new_conv_with_shifting = pd.read_table(
            filepath_or_buffer=rf"{definitions.ROOT_DIR}/tests/test_files/static_checks/"
                               "TRY/UnknownStationID_20150101_20151231_Aachen"
                               "_with_time_shifting.mos",
            header=43,
            sep='\s+',
            skip_blank_lines=False,
            encoding="latin",
        )

        self.new_conv_without_shifting_new_NormDirRad = pd.read_table(
            filepath_or_buffer=rf"{definitions.ROOT_DIR}/tests/test_files/static_checks/TRY"
                               "/UnknownStationID_20150101_20151231_Aachen"
                               "_without_time_shifting_new_DirNormRad.mos",
            header=43,
            sep='\s+',
            skip_blank_lines=False,
            encoding="latin",
        )

        self.new_conv_with_shifting_new_NormDirRad = pd.read_table(
            filepath_or_buffer=rf"{definitions.ROOT_DIR}/tests/test_files/static_checks/TRY/"
                               "UnknownStationID_20150101_20151231_Aachen"
                               "_with_time_shifting_new_DirNormRad.mos",
            header=43,
            sep='\s+',
            skip_blank_lines=False,
            encoding="latin",
        )

        self.new_conv_passthrough_new_NormDirRad = pd.read_table(
            filepath_or_buffer=rf"{definitions.ROOT_DIR}/tests/test_files/static_checks/TRY/"
                               "UnknownStationID_20150101_20151231_Aachen"
                               "_passthrough_new_DirNormRad.mos",
            header=43,
            sep='\s+',
            skip_blank_lines=False,
            encoding="latin",
        )

        header = [
            "timeOfYear",
            "DryBulbTemp",
            "DewPointTemp",
            "RelHum",
            "AtmPressure",
            "ExtHorRad",
            "ExtDirNormRad",
            "HorInfra",
            "GlobHorRad",
            "DirNormRad",
            "DiffHorRad",
            "GlobHorIll",
            "DirecNormIll",
            "DiffuseHorIll",
            "ZenithLum",
            "WindDir",
            "WindSpeed",
            "TotalSkyCover",
            "OpaqueSkyCover",
            "Visibility",
            "CeilingH",
            "WeatherObs",
            "WeatherCode",
            "PrecWater",
            "Aerosol",
            "Snow",
            "DaysSinceSnow",
            "Albedo",
            "LiquidPrecD",
            "LiquidPrepQuant",
        ]

        self.old_conv.columns = header
        self.new_conv_no_shifting.columns = header
        self.new_conv_with_shifting.columns = header
        self.new_conv_without_shifting_new_NormDirRad.columns = header
        self.new_conv_with_shifting_new_NormDirRad.columns = header
        self.new_conv_passthrough_new_NormDirRad.columns = header

        c = ProjectClassTRY(
            os.path.join(
                definitions.ROOT_DIR,
                "core",
                "tests",
                "test_files",
                "static_checks",
                "TRY",
                "TRY2015_507931060546_Jahr.dat",
            )
        )
        c.import_data()

        self.raw = c.imported_data

    def test_TRY_shifting(self):
        self.load_files()

        shift_diff = self.new_conv_no_shifting - self.new_conv_with_shifting

        # comparison of a variable that is not shifted
        value_compare_noshift = self.raw["WG"].iloc[31:41]
        value_compare_noshift = pd.concat(
            [
                value_compare_noshift.reset_index(drop=True),
                self.new_conv_no_shifting["WindSpeed"]
                .iloc[30:40]
                .reset_index(drop=True),
                self.new_conv_with_shifting["WindSpeed"]
                .iloc[30:40]
                .reset_index(drop=True),
            ],
            ignore_index=True,
            axis=1,
        )

        # comparison of a variable that is shifted back and forth (raw = mos measurement time)
        value_compare = self.raw["D"].iloc[31:43]
        value_compare = pd.concat(
            [
                value_compare.reset_index(drop=True),
                self.new_conv_no_shifting["DiffHorRad"]
                .iloc[30:42]
                .reset_index(drop=True),
                self.new_conv_with_shifting["DiffHorRad"]
                .iloc[30:42]
                .reset_index(drop=True),
            ],
            ignore_index=True,
            axis=1,
        )

        print("")

    def test_TRY_Old_vs_newWithoutShifting(self):
        """comparison of an old vs no shift vs shift"""

        self.load_files()

        diff_1 = self.old_conv - self.new_conv_no_shifting
        diff_2 = self.old_conv - self.new_conv_with_shifting

        value_compare_1 = pd.concat(
            [
                self.old_conv["DirNormRad"].iloc[30:45].reset_index(drop=True),
                self.new_conv_no_shifting["DirNormRad"]
                .iloc[30:45]
                .reset_index(drop=True),
                self.new_conv_with_shifting["DirNormRad"]
                .iloc[30:45]
                .reset_index(drop=True),
            ],
            ignore_index=True,
            axis=1,
        )

        value_compare_2 = pd.concat(
            [
                self.old_conv["WindSpeed"].iloc[30:40].reset_index(drop=True),
                self.new_conv_no_shifting["WindSpeed"]
                .iloc[30:40]
                .reset_index(drop=True),
                self.new_conv_with_shifting["WindSpeed"]
                .iloc[30:40]
                .reset_index(drop=True),
            ],
            ignore_index=True,
            axis=1,
        )

        value_compare_3 = pd.concat(
            [
                self.old_conv["GlobHorRad"].iloc[30:40].reset_index(drop=True),
                self.new_conv_no_shifting["GlobHorRad"]
                .iloc[30:40]
                .reset_index(drop=True),
                self.new_conv_with_shifting["GlobHorRad"]
                .iloc[30:40]
                .reset_index(drop=True),
            ],
            ignore_index=True,
            axis=1,
        )

        value_compare_4 = pd.concat(
            [
                self.old_conv["DiffHorRad"].iloc[30:40].reset_index(drop=True),
                self.new_conv_no_shifting["DiffHorRad"]
                .iloc[30:40]
                .reset_index(drop=True),
                self.new_conv_with_shifting["DiffHorRad"]
                .iloc[30:40]
                .reset_index(drop=True),
            ],
            ignore_index=True,
            axis=1,
        )

        value_compare_5 = pd.concat(
            [
                self.raw["B"].iloc[31:41].reset_index(drop=True),
                self.old_conv["DirNormRad"].iloc[30:40].reset_index(drop=True),
                self.new_conv_no_shifting["DirNormRad"]
                .iloc[30:40]
                .reset_index(drop=True),
                self.new_conv_with_shifting["DirNormRad"]
                .iloc[30:40]
                .reset_index(drop=True),
                self.new_conv_without_shifting_new_NormDirRad["DirNormRad"]
                .iloc[30:40]
                .reset_index(drop=True),
                self.new_conv_with_shifting_new_NormDirRad["DirNormRad"]
                .iloc[30:40]
                .reset_index(drop=True),
                self.new_conv_passthrough_new_NormDirRad["DirNormRad"]
                .iloc[30:40]
                .reset_index(drop=True),
            ],
            ignore_index=True,
            axis=1,
        )

        # shifting is quite intense effect for direct radiation see value_compare_5
        # -> that is why the pass-through handling is introduced

        print("")
