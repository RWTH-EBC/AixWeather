import datetime as dt

# choose the project class according to the desired weather data origin
from project_class import ProjectClassDWDHistorical
from core.data_quality_checks import plot_heatmap_missing_values_daily


# initiate the project class which contains or creates all variables and functions
DWD_pull_project = ProjectClassDWDHistorical(
    start=dt.datetime(2022, 1, 1),
    end=dt.datetime(2023, 1, 1),
    station=15000,
    fillna=True,
)

# import historical weather from the DWD open access database
DWD_pull_project.import_data()
print(f"\nHow the imported data looks like:\n{DWD_pull_project.imported_data.head()}\n")

# convert this imported data to the core format
DWD_pull_project.data_2_core_data()
print(f"\nHow the core data looks like:\n{DWD_pull_project.core_data.head()}\n")

# you may also use data quality check utils, like:
plot_heatmap_missing_values_daily(DWD_pull_project.core_data)

# convert this core data to an output data format of your choice
DWD_pull_project.core_2_csv()
DWD_pull_project.core_2_json()
DWD_pull_project.core_2_pickle()
DWD_pull_project.core_2_mos()
DWD_pull_project.core_2_epw()