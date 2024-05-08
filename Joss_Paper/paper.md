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

AixWeather is a versatile weather data generation tool designed to simplify the process of acquiring, 
formatting, and exporting weather data for building energy system simulations. 
It addresses the challenges researchers and industry players face in obtaining accurate and standardized weather 
data by providing a user-friendly platform.

Key Features:
Data Transformation: AixWeather can seamlessly convert weather data from various sources into a 
standardized core format and from there to the desired export format.
Data Accuracy: AixWeather ensures data accuracy by considering critical and often overlooked factors such as time zones, 
time reference of measurement, 
unit conversions, missing data points, and avoiding interpolation-induced smoothing. Additionally, 
it leverages physical relationships to calculate missing weather variables from available data.
Flexibility: The tool offers a generic framework that allows for the effortless addition of 
new import and output formats, enhancing its adaptability for diverse weather data requirements.
Modelica ReaderTMY3 Compatibility: A standout feature of AixWeather is its support for generating weather data 
compatible with the Modelica ReaderTMY3 format, addressing a specific and underserved need in the field.

AixWeather empowers researchers and professionals working in building energy systems by streamlining 
the weather data generation process. It ensures the availability of high-quality weather data, enabling researchers 
to focus on their essential work in the field of building energy systems.

\autoref{fig:AixWeatherStructure}

![Structure of AixWeather.\label{fig:AixWeatherStructure}](Overview_WeatherTool.drawio.png)


# Statement of need

Building energy simulations are crucial for research building energy systems, 
often relying on specific weather data formats. Creating such weather data can be a 
labor-intensive and error-prone task. AixWeather addresses these challenges by offering 
a comprehensive solution for pulling, transforming, and exporting weather data from various sources and formats.

There are limited tools available for importing and converting real weather data or Test Reference Years (TRY). 
Also, there is a lack of tools supporting the ReaderTMY3 format.
AixWeather offers a practical solution to a critical need in the field, making it a 
valuable tool for researchers working with this specific output format.
The ReaderTMY3 is a modelica model of the well established open source library Buildings
[@WetterZuoNouiduiPang.2014].
Other libraries such as the open source library AixLib [@Maier.2023] import this model
to handle weather data.

# Acknowledgements

We acknowledge contributions from Michael Mans, Felix Nienaber and Ana Constantin for providing functional base code.
We also want to thank Felix Rehmann and Firas Drass from the TU Berlin for their support on the WebApp.
David Jansen and Fabian Wüllhorst supported with the quality management through continuous integration.

# References