---
title: 'AixWeather: A weather data generation tool for building energy system simulations. Pull, Transform, Export.'
tags:
  - Python
  - Weather
  - Weather data generation
  - Weather data transformation
  - Building energy system simulation
  - AixLib
authors:
  - name: Martin Rätz
    orcid: 0000-0002-3573-2872
    affiliation: 1
affiliations:
 - name: Institute for Energy Efficient Buildings and Indoor Climate, E.ON Energy Research Center, RWTH Aachen University, Germany
   index: 1
date: 15 September 2023
bibliography: paper.bib
---

# Summary

AixWeather is a tool for generating weather data for building energy system simulations. 
It can be used to retrieve, format, enrich and ultimately export weather data in various file formats, 
including .epw (EnergyPlus) and .mos (AixLib).
It addresses the challenges researchers and industry players face in obtaining accurate and standardized weather 
data by providing a streamlined process.

**Key features of AixWeather**:

*Data retrieval*: AixWeather can directly retrieve data from the german weather provider DWD, and 
supports historical, recent and forecasted weather data retrieval. It also supports the upload 
of test reference years (TRY) from the DWD and .epw files from EnergyPlus. A custom weather data 
upload is also supported, which depending on the data structure, needs to be adjusted by the user.

*Data conversion*: AixWeather converts this raw weather data from various sources into a 
standardized 
core format and from there into the desired export format.

*Data accuracy*: AixWeather ensures data accuracy by taking into account critical factors that are 
often overlooked in custom solutions, including consideration of time zones, 
the time reference of the measurement, unit conversions, correct handling of incomplete data series 
and, where possible, the avoidance of interpolation-related smoothing.

*Data enrichment*: AixWeather uses physical relationships to calculate missing weather variables
from the available weather data and metadata.

*Flexibility*: AixWeather offers a modular structure that simplifies the addition of new import and
output formats. The maintenance of existing formats is also simplified, 
enabling a faster response to changing weather data formats.

*Modelica ReaderTMY3 compatibility*: A special feature of AixWeather is its support for generating 
weather data compatible with the Modelica ReaderTMY3 format. This covers a so far unsatisfied need.

AixWeather can be accessed through the repository itself, or through the web application at 
https://aixweather.eonerc.rwth-aachen.de.
The web application is also open source and hosted in a separate repository at 
https://github.com/RWTH-EBC/AixWeather-WebApp.
The web application provides a user-friendly interface
for even more convenient generation of weather data without the need of setting up an environment.

AixWeather empowers researchers and professionals working in building energy systems by streamlining 
the weather data generation process. It ensures the availability of high-quality weather data, 
enabling researchers to focus on their essential work in the field of building energy systems.

Figure \autoref{fig:AixWeatherStructure} shows the current structure of AixWeather. 
Starting from the import layer, the data is transformed into a core format, and from there into the
desired export format. The core format is a standardized format that allows for easy conversion to
different export formats. The pass-through handling avoids avoidable interpolation-related 
smoothing, through storing the original unsmoothed time series and, if the shifting sequence 
allows, overwriting the smoothed time series in the output file.

![Structure of AixWeather.\label{fig:AixWeatherStructure}](Overview_WeatherTool.png)


# Statement of need

Building energy simulations, crucial for research in building energy systems, 
often rely on specific weather data formats. Creating such weather data can be a 
labor-intensive and error-prone task. AixWeather addresses these challenges by offering 
a comprehensive solution for pulling, transforming, enriching and exporting weather data from 
various sources and formats.

There are tools that focus on generating typical meteorological year (TMY) data, like the PVGIS [@PVGIS.2023]
from the European Commission, providing TMY exports as .csv, .json and in the .epw format.
EnergyPlus [@EnergyPlus.2017], a widely used building energy simulation tool, also provides a 
weather data converter to cover the needs of its users, again only supporting the .epw format.
There exist only limited tools for importing and converting real, historic or forecast, weather 
data to building energy simulation formats.
The same holds true for Test Reference Years (TRY) from the german weather service (DWD). 
Also, there is a lack of tools supporting conversions to the ReaderTMY3 format.
The ReaderTMY3 is a modelica model of the well established open source library Buildings
[@WetterZuoNouiduiPang.2014].
Other libraries such as the open source library AixLib [@Maier.2023] import this model
to handle weather data.
Often user of these libraries, which do not have an TMY3 file at hand, get stuck or invest a lot of 
time to convert their weather data to the required format.
Solving this problem, was the initial motivation to develop AixWeather.
Now AixWeather also covers the aforementioned needs, making 
it a valuable tool not only for researchers that work with the ReaderTMY3 format.

# Acknowledgements

We acknowledge contributions from Michael Mans, Felix Nienaber and Ana Constantin for providing 
some functional base code.
We also want to thank Firas Drass and Felix Rehmann from the TU Berlin for their support on the 
WebApp.
Last but not least, we want to thank Fabian Wüllhorst and David Jansen for their support with the 
quality management through continuous integration.

# References