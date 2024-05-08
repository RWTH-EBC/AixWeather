"""
Includes functions to convert units in weather data.
"""
import logging

import pandas as pd

logger = logging.getLogger(__name__)


def Jcm2_to_Whm2(radiation: pd.Series):
    """convert radiance unit from J/cm^2 to Wh/m^2"""
    radiation = radiation / 0.36
    logger.debug("%s transformed from from J/cm2 to Wh/m2", radiation.name)
    return radiation


def Jm2_to_Whm2(radiation: pd.Series):
    """convert radiance unit from J/m^2 to Wh/m^2"""
    radiation = radiation / 3600
    logger.debug("%s transformed from from J/m2 to Wh/m2", radiation.name)
    return radiation


def kJm2_to_Whm2(radiation: pd.Series):
    """convert radiance unit from kJ/m^2 to Wh/m^2"""
    radiation = radiation / 3.6
    logger.debug("%s transformed from from kJ/m^2 to Wh/m^2", radiation.name)
    return radiation


def hPa_to_Pa(pressure: pd.Series):
    """convert pressure unit from hPa to Pa"""
    pressure = pressure * 100
    logger.debug("%s transformed from from hPa to Pa", pressure.name)
    return pressure


def eigth_to_tenth(cloudgrade: pd.Series):
    """convert cloudgrade from eighth to tenth"""
    cloudgrade = cloudgrade * 10 / 8
    logger.debug("%s transformed from from eighth to tenth", cloudgrade.name)
    return cloudgrade


def percent_to_tenth(cloudgrade: pd.Series):
    """convert cloudgrade from percent to tenth"""
    cloudgrade = cloudgrade / 10
    logger.debug("%s transformed from from percent to tenth", cloudgrade.name)
    return cloudgrade


def kelvin_to_celcius(temperature: pd.Series):
    """convert temperature from kelvin to celcius"""
    temperature = temperature - 273.15
    logger.debug("%s transformed from from kelvin to celcius", temperature.name)
    return temperature


def divide_by_1000(series: pd.Series):
    """divide by 1000"""
    series = series / 1000
    logger.debug("%s transformed from x to x/1000", series.name)
    return series
