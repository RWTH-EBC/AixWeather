"""
Includes functions to convert units in weather data.
"""

import pandas as pd


def Jcm2_to_Whm2(radiation: pd.Series):
    """convert radiance unit from J/cm^2 to Wh/m^2"""
    radiation = radiation / 0.36
    print(f"{radiation.name} transformed from from J/cm2 to Wh/m2")
    return radiation


def Jm2_to_Whm2(radiation: pd.Series):
    """convert radiance unit from J/m^2 to Wh/m^2"""
    radiation = radiation / 3600
    print(f"{radiation.name} transformed from from J/m2 to Wh/m2")
    return radiation


def kJm2_to_Whm2(radiation: pd.Series):
    """convert radiance unit from kJ/m^2 to Wh/m^2"""
    radiation = radiation / 3.6
    print(f"{radiation.name} transformed from from kJ/m^2 to Wh/m^2")
    return radiation


def hPa_to_Pa(pressure: pd.Series):
    """convert pressure unit from hPa to Pa"""
    pressure = pressure * 100
    print(f"{pressure.name} transformed from from hPa to Pa")
    return pressure


def eigth_to_tenth(cloudgrade: pd.Series):
    """convert cloudgrade from eighth to tenth"""
    cloudgrade = cloudgrade * 10 / 8
    print(f"{cloudgrade.name} transformed from from eighth to tenth")
    return cloudgrade


def percent_to_tenth(cloudgrade: pd.Series):
    """convert cloudgrade from percent to tenth"""
    cloudgrade = cloudgrade / 10
    print(f"{cloudgrade.name} transformed from from percent to tenth")
    return cloudgrade


def kelvin_to_celcius(temperature: pd.Series):
    """convert temperature from kelvin to celcius"""
    temperature = temperature - 273.15
    print(f"{temperature.name} transformed from from kelvin to celcius")
    return temperature


def divide_by_1000(series: pd.Series):
    """divide by 1000"""
    series = series / 1000
    print(f"{series.name} transformed from x to x/1000")
    return series
