"""
AixWeather-Module. See readme or documentation for more information.
"""
import pandas as pd
from packaging.version import Version
import warnings

if Version(pd.__version__) > Version("2.1"):
    warnings.warn("pandas versions >2.2 lead to wrong .eps and .mos results, consider downgrading to 2.1")

__version__ = '0.1.6'
