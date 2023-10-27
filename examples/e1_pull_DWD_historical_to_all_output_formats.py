"""Contains examples"""

# pylint: disable=C0415, C0103
# let pylint ignore to import from aixweather (Import outside toplevel), and ignore that pylint
# suggests e1_pull_DWD_historical_to_all_output_formats would not be snake_case.

import datetime as dt

def e1_pull_DWD_historical_to_all_output_formats():
    """
    1. Learn how to use `AixWeather`
    2. See examplary use of additional features and settings
    3. Create weather data files
    """
    # choose the project class according to the desired weather data origin
    from aixweather.project_class import ProjectClassDWDHistorical

    # initiate the project class which contains or creates all variables and functions
    DWD_pull_project = ProjectClassDWDHistorical(
        start=dt.datetime(2022, 1, 1),
        end=dt.datetime(2023, 1, 1),
        station=433,
        # specify whether nan-values should be filled when exporting
        fillna=True,
        # define results path if desired
        abs_result_folder_path=None,
    )

    # import historical weather from the DWD open access database
    DWD_pull_project.import_data()
    print(
        f"\nHow the imported data looks like:\n{DWD_pull_project.imported_data.head()}\n"
    )

    # convert this imported data to the core format
    DWD_pull_project.data_2_core_data()
    print(f"\nHow the core data looks like:\n{DWD_pull_project.core_data.head()}\n")

    # you may also use data quality check utils, like:
    from aixweather.data_quality_checks import plot_heatmap_missing_values_daily

    # plot data quality
    plot = plot_heatmap_missing_values_daily(DWD_pull_project.core_data)
    plot.show()

    # convert this core data to an output data format of your choice
    DWD_pull_project.core_2_csv()
    DWD_pull_project.core_2_json()
    DWD_pull_project.core_2_pickle()
    DWD_pull_project.core_2_mos()
    DWD_pull_project.core_2_epw()


if __name__ == "__main__":
    e1_pull_DWD_historical_to_all_output_formats()

    print("\nExample 1: That´s it! :)")
