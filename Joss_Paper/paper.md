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

Building simulations are one of the main tools for building energy system research.
These simulations require weather data, often in a very specific format.
The creation of such weather data can be tedious and error prone.
`AixWeather` will help to pull, transform and export weather data from one source or format origin to another, 
while respecting commonly overseen issues like: 
time zone, 
time of measurement, 
avoidance of smoothing through interpolation,
unit transformation,
missing data points,
and calculates missing weather variables from other available variables.




\autoref{fig:AixWeatherStructure}

![Structure of AixWeather.\label{fig:AixWeatherStructure}](docs/Overview_WeatherTool.drawio.png)



# Statement of need

Building simulations are one of the main tools for building energy system research.
These simulations often require weather data, often in a very specific format.
The creation of such weather data can be tedious and error prone.

`AixWeather` was designed to be used by both researchers and researching industry.

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