
# AixWeather Tutorial

This example is a step-by-step guide to pull historical weather data from the DWD open access database
and convert it to different output formats.
Thus showing all possible steps on how to use AixWeather.
To run the tool for other weather data sources, just change the project class.
The rest of the code is streamlined and will remain the same.

Enable logging, this is just to get more feedback through the terminal

```python
import logging

logging.basicConfig(level="DEBUG")
```

Choose the project class according to the desired weather data origin.
Check the project_class.py file or the API documentation to see which classes are available.
[project classes](https://rwth-ebc.github.io/AixWeather//main//docs/code/aixweather.html#module-aixweather.project_class)

```python
from aixweather.project_class import ProjectClassDWDHistorical
```

Step 0: Initiate the project class which contains or creates all variables and functions.
For this, we use the datetime module to specify dates.

```python
import datetime as dt

project = ProjectClassDWDHistorical(
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
project.import_data()
print(f"\nHow the imported data looks like:\n{project.imported_data.head()}\n")
```

Step 2: Convert this imported data to the core format

```python
project.data_2_core_data()
print(f"\nHow the core data looks like:\n{project.core_data.head()}\n")
```

You may optionally also use data quality check utils, like:

```python
from aixweather.data_quality_checks import plot_heatmap_missing_values
```

Plot data quality

```python
plot = plot_heatmap_missing_values(project.core_data)
plot.show()
```

Step 3: Convert this core data to an output data format of your choice

```python
project.core_2_csv()
project.core_2_json()
project.core_2_pickle()
project.core_2_mos()
project.core_2_epw()
```

By the way, if you want to run this with some other weather data source, here are some copy-paste snippets to get you started:

For DWD Forecast data

```python
from aixweather.project_class import ProjectClassDWDForecast

project = ProjectClassDWDForecast(
    station="06710",  # Example station: Lausanne
    abs_result_folder_path=None,  # Optional: specify result path
)
```

For EPW and TRY we need to import the .epw or .dat file, e.g. from your local drive. The
Readme provides information on where you can download your own EPW and TRY files. For this
example, we use the test files provided in the tests folder (be sure to have the full
repository downloaded to have access to these files).
If you use your own files, you can specify the path to the file in the `path` argument.

These imports are just to create the path to the file stored in the tests folder

```python
import os
from aixweather import definitions
```

For EPW files

```python
from aixweather.project_class import ProjectClassEPW

project = ProjectClassEPW(
    path=os.path.join(
        definitions.ROOT_DIR,
        "tests/test_files/regular_tests/EPW/test_EPW_Essen_Ladybug/input/DEU_NW_Essen_104100_TRY2035_05_Wint_BBSR.epw",
    ),  # Example: EPW weather file for Essen
    abs_result_folder_path=None,
)
```

For TRY (Test Reference Year) data

```python
from aixweather.project_class import ProjectClassTRY

project = ProjectClassTRY(
    path=os.path.join(
        definitions.ROOT_DIR,
        "tests/test_files/regular_tests/TRY/test_TRY2015/input/TRY2015_507931060546_Jahr.dat"
    ),
)
```
