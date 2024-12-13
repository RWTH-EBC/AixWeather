# Tutorial and Example

This folder contains example files which help with the understanding of AixWeather.

### `e1_pull_DWD_historical_to_all_output_formats.py`

1. Learn how to use `AixWeather`
2. Create weather data files

The streamlined workflow to use AixWeather locally is always as follows:

1. Create a project class instance of your choice depending on the desired weather data origin
2. Run the command to import data
3. Run the command to transform data (to the core format)
4. Run the command to export data (which is actually a transformation from the core format to the desired output format)
