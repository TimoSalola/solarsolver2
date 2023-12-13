import math

import pvlib.atmosphere

from pvlib import location, irradiance

"""
Astronomical functions
Currently supports angle of incidence and solar angle estimations.

Angle of incidence is the angle between the solar panel normal angle and the angle of sunlight hitting the panel.
Solar azimuth and Zenith are the spherical coordinate angles used for describing the angle of the sun.

Both angles are useful for reflection and geometric projection functions.

"""


def get_solar_angle_of_incidence(dt, latitude, longitude, tilt, azimuth):
    """
    Estimates solar angle of incidence at given datetime. Other parameters, tilt, azimuth and geolocation are from
    config.py.
    :param latitude:
    :param longitude:
    :param azimuth:
    :param tilt:
    :param dt: Datetime object, should include date and time.
    :return: Angle of incidence in degrees. Angle between sunlight and solar panel normal
    """

    solar_azimuth, solar_apparent_zenith = get_solar_azimuth_zenit(dt, latitude, longitude)
    panel_tilt = tilt
    panel_azimuth = azimuth

    # angle of incidence, angle between direct sunlight and solar panel normal
    angle_of_incidence = irradiance.aoi(panel_tilt, panel_azimuth, solar_apparent_zenith, solar_azimuth)

    # setting upper limit of 90 degrees to avoid issues with projection functions. If light comes with an angle of 90
    # deg aoi, none should be absorbed. The same goes with angles of 90+deg
    if angle_of_incidence > 90:
        return 90

    return angle_of_incidence


def get_air_mass(time, latitude, longitude):
    """
    Generates air mass at time + solar zenith angle by using the default model
    :param latitude:
    :param longitude:
    :param time:
    :return:
    """

    solar_zenith = get_solar_azimuth_zenit(time, latitude, longitude)[1]




    # acceptable solar zenith(sun distance from zenith)
    air_mass = pvlib.atmosphere.get_relative_airmass(solar_zenith)

    # airmass equation returns nan if solar zenit >90
    # apperently max airmass is near 40 so we can just return 40 here in order to avoid nan values
    # another option
    if math.isnan(air_mass):
        return 40

    """
    print("time:")
    print(time)
    print("latitude:")
    print(latitude)
    print("longitude:")
    print(longitude)
    print("solar zenith")
    print(solar_zenith)
    print("airmass")
    print(air_mass)
    """


    return air_mass


def get_solar_azimuth_zenit(dt, latitude, longitude):
    """
    Returns apparent solar zenith and solar azimuth angles in degrees.
    :param longitude:
    :param latitude:
    :param dt: time to compute the solar position for.
    :return: azimuth, zenith
    """

    # panel location and installation parameters from config file
    panel_latitude = latitude
    panel_longitude = longitude

    # panel location object, required by pvlib
    panel_location = location.Location(panel_latitude, panel_longitude, tz="UTC")

    # solar position object
    solar_position = panel_location.get_solarposition(dt)

    # apparent zenith and azimuth, Using apparent for zenith as the atmosphere affects sun elevation.
    solar_apparent_zenith = solar_position["apparent_zenith"].values[0]
    solar_azimuth = solar_position["azimuth"].values[0]

    return solar_azimuth, solar_apparent_zenith


def __debug_add_solar_angles_to_df(df, latitude, longitude, tilt, azimuth):
    def helper_add_zenith(data):
        s_azimuth, s_zenith = get_solar_azimuth_zenit(data["time"], latitude, longitude)
        return s_zenith

    # applying helper function to dataset and storing result as a new column
    df["zenith"] = df.apply(helper_add_zenith, axis=1)

    def helper_add_azimuth(data):
        s_azimuth, s_zenith = get_solar_azimuth_zenit(data["time"], latitude, longitude)
        return s_azimuth

    # applying helper function to dataset and storing result as a new column
    df["azimuth"] = df.apply(helper_add_azimuth, axis=1)

    def helper_add_aoi(data):
        aoi = get_solar_angle_of_incidence(data["time"], latitude, longitude, tilt, azimuth)
        return aoi

    # applying helper function to dataset and storing result as a new column
    df["aoi"] = df.apply(helper_add_aoi, axis=1)

    return df
