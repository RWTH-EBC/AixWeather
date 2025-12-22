"""
This script tests the impact of changes on the simulation with the TMYReader in AixLib.
"""

import pytest
import unittest


@pytest.mark.dymola
class TestAnotherDymolaFeature:
    def test_feature_x(self):
        assert True
