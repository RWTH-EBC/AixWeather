# conftest.py
import pytest


def pytest_addoption(parser):
    """
    Add a command line option to enable Dymola tests.
    """
    parser.addoption(
        "--dymola",
        action="store_true",
        default=False,
        help="Run tests that require Dymola installation."
    )


def pytest_configure(config):
    """
    Register the custom marker to avoid warnings.
    """
    config.addinivalue_line("markers", "dymola: mark test as requiring Dymola")


def pytest_collection_modifyitems(config, items):
    """
    This hook runs after test collection is complete.
    It iterates over items and marks them to be skipped if necessary.
    """
    run_dymola = config.getoption("--dymola")

    # Define the skip marker
    skip_dymola = pytest.mark.skip(reason="Skipping Dymola test (use --dymola to run)")

    for item in items:
        # Check if the test is part of a class named 'DymolaTest'
        # or has the explicit @pytest.mark.dymola marker
        is_dymola_test = "dymola" in item.keywords

        if is_dymola_test:
            # If we are NOT in Dymola mode, skip the test
            if not run_dymola:
                item.add_marker(skip_dymola)
        else:
            # If we ARE in Dymola mode, we might want to skip standard tests
            # to ONLY run Dymola tests (as requested).
            if run_dymola:
                item.add_marker(pytest.mark.skip(reason="Skipping non-Dymola test in Dymola mode"))
