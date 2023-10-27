"""
AixWeather Transformation to Core Data

The 'transformation_to_core_data' module contains functions to transform imported weather data to a
standardized core data format within the AixWeather package (see auxiliary.py).

This core data format adheres to specific guidelines:

- Timezone: UTC
- Hourly data
- Index is a datetime index (DatetimeIndex complete and monotonic)
- Measurement at the indicated time (not as average for the following or preceding hour)
- Always the same set of variables names (see core_data)
- Missing values are displayed as 'nan'

These transformation functions take imported_data as input and convert it to the specified core data format,
ensuring uniformity and adherence to the core data guidelines.

Each module is designed to handle data from a specific source or format.
"""
