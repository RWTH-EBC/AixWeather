
```python
import datetime as dt
```

choose the project class according to the desired weather data origin

```python
from aixweather.project_class import ProjectClassDWDHistorical
```

initiate the project class which contains or creates all variables and functions

```python
DWD_pull_project = ProjectClassDWDHistorical(
    start=dt.datetime(2022, 1, 1),
    end=dt.datetime(2023, 1, 1),
    station=15000,
    # specify whether nan-values should be filled when exporting
    fillna=True,
    # define results path if desired
    abs_result_folder_path=None
)
```

import historical weather from the DWD open access database

```python
DWD_pull_project.import_data()
print(f"\nHow the imported data looks like:\n{DWD_pull_project.imported_data.head()}\n")
```

convert this imported data to the core format

```python
DWD_pull_project.data_2_core_data()
print(f"\nHow the core data looks like:\n{DWD_pull_project.core_data.head()}\n")
```

you may also use data quality check utils, like:

```python
from aixweather.data_quality_checks import plot_heatmap_missing_values_daily
```

plot data quality

```python
plot_heatmap_missing_values_daily(DWD_pull_project.core_data)
```

convert this core data to an output data format of your choice

```python
DWD_pull_project.core_2_csv()
DWD_pull_project.core_2_json()
DWD_pull_project.core_2_pickle()
DWD_pull_project.core_2_mos()
DWD_pull_project.core_2_epw()
```
