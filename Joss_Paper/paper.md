---
title: 'AixWeather: A weather data generation tool for building energy system simulations. Pull, Transform, Export.'
tags:
  - Python
  - weather
  - simulation
  - building energy system
  - AixLib
authors:
  - name: Martin Rätz
    orcid: 0000-0002-3573-2872
    affiliation: 1
affiliations:
 - name: Institute for Energy Efficient Buildings and Indoor Climate, E.ON Energy Research Center, RWTH Aachen University, Germany
   index: 1
date: 13 August 2017
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
AixWeather ensures data accuracy by considering critical and often overlooked factors such as time zones, time reference of measurement, 
unit conversions, missing data points, and avoiding interpolation-induced smoothing. Additionally, 
it leverages physical relationships to calculate missing weather variables from available data.
Flexibility: The tool offers a generic framework that allows for the effortless addition of 
new import and output formats, enhancing its adaptability for diverse weather data requirements.
Modelica TMY3Reader Compatibility: A standout feature of AixWeather is its support for generating weather data 
compatible with the Modelica TMY3Reader format, addressing a specific and underserved need in the field.

AixWeather empowers researchers and professionals working in building energy systems by streamlining 
the weather data generation process. It ensures the availability of high-quality weather data, enabling researchers 
to focus on their essential work in the field of building energy systems.


\autoref{fig:AixWeatherStructure}

![Structure of AixWeather.\label{fig:AixWeatherStructure}](docs/Overview_WeatherTool.drawio.png)



# Statement of need

Building energy simulations are crucial for research building energy systems, 
often relying on specific weather data formats. Creating such weather data can be a 
labor-intensive and error-prone task. AixWeather addresses these challenges by offering 
a comprehensive solution for pulling, transforming, and exporting weather data from various sources and formats.




AixWeather ensures data accuracy by considering critical factors such as time zones, measurement times, 
unit conversions, missing data points, and avoiding interpolation-induced smoothing. Additionally, 
it leverages physical relationships to calculate missing weather variables from available data.

Beyond its core functionalities, AixWeather offers a flexible and extensible framework. 
It simplifies the addition of new import and output formats, making it a versatile tool for researchers 
in the field of building energy systems.



Importing real weather data or Test Reference Years (TRY) data into the Modelica TMY3Reader format 
can be challenging due to format differences. Currently, there are limited tools available for this purpose.

AixWeather offers a practical solution by providing support for generating weather data compatible with the 
Modelica TMY3Reader format. This feature addresses a critical need in the field, making AixWeather a 
valuable tool for researchers working with this specific output format.

Notably, AixWeather stands apart by offering support for the Modelica TMY3Reader format, addressing a specific 
and underserved requirement in the field. This unique feature positions it as an indispensable tool 
for those seeking compatibility with this format.


Building simulations are one of the main tools for building energy system research.
These simulations often require weather data, often in a very specific format.
The creation of such weather data can be tedious and error prone.

`AixWeather` was designed to be used by both researchers and researching industry.
and sophisticated design and operation of energy building systems

# Mathematics

Single dollars ($) are required for inline mathematics e.g. $f(x) = e^{\pi/x}$

Double dollars make self-standing equations:

$$\Theta(x) = \left\{\begin{array}{l}
0\textrm{ if } x < 0\cr
1\textrm{ else}
\end{array}\right.$$

You can also use plain \LaTeX for equations
\begin{equation}\label{eq:fourier}
\hat f(\omega) = \int_{-\infty}^{\infty} f(x) e^{i\omega x} dx
\end{equation}
and refer to \autoref{eq:fourier} from text.

# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures



# Acknowledgements

We acknowledge contributions from Brigitta Sipocz, Syrtis Major, and Semyeong
Oh, and support from Kathryn Johnston during the genesis of this project.

# References