"""Setup.py script for AixWeather"""

import setuptools
import sys

# read the contents of your README file
from pathlib import Path

readme_path = Path(__file__).parent.joinpath("README.md")
long_description = readme_path.read_text()

INSTALL_REQUIRES = [
    "wetterdienst==0.65.0",
    "unidecode==1.3.7",
    "parameterized==0.9.0",
    "geopandas==0.14.0",
    "geopy==2.4.0",
    "pvlib==0.10.2",
    "matplotlib==3.8.1",
    "seaborn==0.13.0",
]

# Add all open-source packages to setup-requires
SETUP_REQUIRES = INSTALL_REQUIRES.copy()

with open(Path(__file__).parent.joinpath("aixweather", "__init__.py"), "r") as file:
    for line in file.readlines():
        if line.startswith("__version__"):
            VERSION = (
                line.replace("__version__", "")
                .split("=")[1]
                .strip()
                .replace("'", "")
                .replace('"', "")
            )

setuptools.setup(
    name="AixWeather",
    version=VERSION,
    description="A weather data generation tool for building energy system simulations."
    "Pull, Transform, Export.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RWTH-EBC/AixWeather",
    download_url=f"https://github.com/RWTH-EBC/AixWeather/archive/refs/tags/{VERSION}.tar.gz",
    author="RWTH Aachen University, E.ON Energy Research Center, "
    "Institute of Energy Efficient Buildings and Indoor Climate",
    author_email="ebc-abos@eonerc.rwth-aachen.de",
    license="BSD 3-Clause",
    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        "Topic :: Scientific/Engineering",
        "Intended Audience :: Science/Research",
        # 'Programming Language :: Python :: 3.7',
        # 'Programming Language :: Python :: 3.8',
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords=["weather", "BES", "converter", "simulation", "building", "energy"],
    packages=setuptools.find_packages(exclude=["tests", "tests.*", "img"]),
    setup_requires=SETUP_REQUIRES,
    install_requires=INSTALL_REQUIRES,
)
