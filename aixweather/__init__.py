"""
AixWeather-Module. See readme or documentation for more information.
"""
import warnings
from packaging.version import Version
import pandas as pd

if Version(pd.__version__) >= Version("2.2"):
    warnings.warn(
        "pandas versions >2.2 lead to wrong .eps and .mos results,"
        " consider downgrading to 2.1"
    )

__version__ = "0.1.6"
