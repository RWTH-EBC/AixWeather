
```python
"""Contains examples"""
```

pylint: disable=C0415, C0103
let pylint ignore to import from aixweather (Import outside toplevel), and ignore that pylint
suggests e1_pull_DWD_historical_to_all_output_formats would not be snake_case.

```python
import datetime as dt
```

Enable logging, this is just get more feedback through the terminal

```python
import logging
logging.basicConfig(level="DEBUG")
```

Choose the project class according to the desired weather data origin.
Check the project classes file or the API documentation to see which classes are available.

```python
from aixweather.project_class import ProjectClassDWDHistorical
```

Step 0: Initiate the project class which contains or creates all variables and functions.

```python
DWD_pull_project = ProjectClassDWDHistorical(
    start=dt.datetime(2022, 1, 1),
    end=dt.datetime(2023, 1, 1),
    station=15000,
    # specify whether nan-values should be filled when exporting
    fillna=True,
    # define results path if desired
    abs_result_folder_path=None,
)
```

Step 1: Import historical weather from the DWD open access database

```python
DWD_pull_project.import_data()
print(
    f"\nHow the imported data looks like:\n{DWD_pull_project.imported_data.head()}\n"
)
```

Step 2: Convert this imported data to the core format

```python
DWD_pull_project.data_2_core_data()
print(f"\nHow the core data looks like:\n{DWD_pull_project.core_data.head()}\n")
```

you may also use data quality check utils, like:

```python
from aixweather.data_quality_checks import plot_heatmap_missing_values
```

plot data quality

```python
plot = plot_heatmap_missing_values(DWD_pull_project.core_data)
plot.show()
```

Step 3: Convert this core data to an output data format of your choice

```python
DWD_pull_project.core_2_csv()
DWD_pull_project.core_2_json()
DWD_pull_project.core_2_pickle()
DWD_pull_project.core_2_mos()
DWD_pull_project.core_2_epw()
```
