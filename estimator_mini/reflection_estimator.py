"""
REFLECTION FUNCTIONS

Functions for estimating how much of the solar irradiance is absorbed by solar panels in opposed to being reflected away
Equation for radiation absorbed:
Radiation_absorbed = (1-dni_reflected)DNIPOA+(1-ghi_reflected)GHIPOA + (1-diffuse_reflected)DHIPOA
dni_reflected is alpha_BN in notes
ghi_reflected is alpha_dg in notes
diffuse_reflected is alpha_d in notes
"""

import math
import time

import numpy
import astronomical_calculations


def components_to_corrected_poa(DNI_component, DHI_component, GHI_component, dt, lat, lon, tilt, azimuth):
    """
    Takes dni, dhi and ghi components of a solar panel projected irradiance and computes how much of the radiation is
    absorbed by the solar panels, in opposed to reflected away.
    :param azimuth:
    :param tilt:
    :param lon:
    :param lat:
    :param DNI_component: poa transposed dni value(W)
    :param DHI_component: poa transposed dhi value(W)
    :param GHI_component: poa transposed ghi value(W)
    :param dt: time for estimation. For example, "2023-10-13 19:30:00+00:00"
    :return: absorbed radiation in W
    """

    # direct sunlight reflection variable, has to be computed multiple times.

    dni_reflected = __dni_reflected(dt, lat, lon, tilt, azimuth)


    # These values do not have to be recomputed every single time as they are installation-specific, and they do not
    # even take time as an input. This could be optimized if needed.
    dhi_reflected = __dhi_reflected(tilt)

    ghi_reflected = __ghi_reflected(azimuth)


    # POA_reflection_corrected or radiation absorbed by the solar panel.
    POA_reflection_corrected = ((1 - dni_reflected) * DNI_component + (1 - dhi_reflected) * DHI_component +
                                (1 - ghi_reflected) * GHI_component)




    return POA_reflection_corrected


def add_reflection_corrected_poa_to_df(df, lat, lon, tilt, azimuth):
    """
    Adds reflection corrected POA value to dataframe with name "poa_ref_cor"
    :param tilt:
    :param lon:
    :param lat:
    :param azimuth:
    :param df:
    :return:
    """

    # print("Adding reflection corrected POA to dataframe")

    # helper function + apply — structure

    # time1 = current_milli_time()
    def helper_components_to_corrected_poa_fast(dni_poa, dhi_poa, ghi_poa, timestamp):
        return components_to_corrected_poa(dni_poa, dhi_poa, ghi_poa, timestamp, lat, lon, tilt, azimuth)

    df["poa_ref_cor"] = helper_components_to_corrected_poa_fast(df["dni_poa"], df["dhi_poa"], df["ghi_poa"], df["time"])
    # time2 = current_milli_time()

    # print("# total reflection correction time: " + str(time2 - time1) + " ms")

    # print("Reflection corrected POA values added.")

    return df


def add_reflection_corrected_poa_components_to_df(df, latitude, longitude, tilt, azimuth):
    def helper_add_dni_ref(data):
        #  (1-alpha_BN)*BTN
        return math.fabs(1 - __dni_reflected(df["time"], latitude, longitude, tilt, azimuth)) * data["dni_poa"]

    def helper_add_dhi_ref(data):
        # (1-alpha_d)*DT
        return math.fabs(1 - __dhi_reflected(tilt)) * data["dhi_poa"]

    def helper_add_ghi_ref(data):
        # (1-alpha_dg)*DTg
        return math.fabs(1 - __ghi_reflected(tilt)) * data["ghi_poa"]

    """
    BTN = dni_poa
    DTg = ghi_poa
    DT = dhi_poa
    """
    df["dni_rc"] = df.apply(helper_add_dni_ref, axis=1)
    df["dhi_rc"] = df.apply(helper_add_dhi_ref, axis=1)
    df["ghi_rc"] = df.apply(helper_add_ghi_ref, axis=1)

    return df


def __dni_reflected(dt, latitude, longitude, tilt, azimuth):
    """
    Computes a constant in range [0,1] which represents how much of the direct irradiance is reflected from panel
    surfaces.
    :param dt: datetime
    :return: reflected radiation in range [0,1]

    dni_reflected denoted as alpha_BN in Williams work.
    """

    a_r = 0.159  # empirical constant for polycrystalline silicon module reflectance

    # sun angle components
    azimuth_sun, zenith_sun = astronomical_calculations.get_solar_azimuth_zenit(dt, latitude, longitude)
    azimuth_sun = numpy.radians(azimuth_sun)
    zenith_sun = numpy.radians(zenith_sun)

    # panel angles
    panel_tilt = numpy.radians(tilt)
    panel_azimuth = numpy.radians(azimuth)

    # helper variable
    cos_theta_i = math.cos(zenith_sun) * math.cos(panel_tilt) + math.sin(zenith_sun) * math.sin(panel_tilt) * math.cos(
        azimuth_sun - panel_azimuth)

    # upper section of the fraction equation
    upper_fraction = math.e ** (-cos_theta_i / a_r) - math.e ** (-1.0 / a_r)
    # lower section of the fraction equation
    lower_fraction = 1.0 - math.e ** (-1.0 / a_r)

    # fraction or alpha_BN or dni_reflected
    dni_reflected = upper_fraction / lower_fraction

    return dni_reflected


def __ghi_reflected(tilt):
    """
    Computes a constant in range [0,1] which represents how much of ground reflected irradiation is reflected away from
    solar panel surfaces. Note that this is constant for an installation.
    :return: [0,1] float, 0 no light reflected, 1 no light absorbed by panels.

    ghi reflected is denoted as alpha_d in Williams work
    """

    # constants
    c1 = 4.0 / (3.0 * math.pi)

    c2 = -0.074
    a_r = 0.159
    panel_tilt = numpy.radians(tilt)  # theta_T

    # equation parts, part 1 is used 2 times
    part1 = math.sin(panel_tilt) + (panel_tilt - math.sin(panel_tilt)) / (1.0 - math.cos(panel_tilt))

    part2 = c1 * part1 + c2 * (part1 ** 2.0)
    part3 = (-1.0 / a_r) * part2

    ghi_reflected = math.e ** part3

    return ghi_reflected


def __dhi_reflected(tilt):
    """
    Computes a constant in range [0,1] which represents how much of atmospheric diffuse light is reflected away from
    solar panel surfaces. Constant for an installation. Almost a 1 to 1 copy of __ghi_reflected except
    "pi -" addition to part1 and "1-cos" to "1+cos" replacement in part1 as well.
    :return: [0,1] float, 0 no light reflected, 1 no light absorbed by panels.

    # denoted as alpha_BN in williams work
    """
    # constants

    c1 = 4.0 / (math.pi * 3.0)
    c2 = -0.074
    a_r = 0.159
    panel_tilt = numpy.radians(tilt)  # theta_T
    pi = math.pi

    # equation parts, part 1 is used 2 times
    part1 = math.sin(panel_tilt) + (pi - panel_tilt - math.sin(panel_tilt)) / (1.0 + math.cos(panel_tilt))

    part2 = c1 * part1 + c2 * (part1 ** 2.0)
    part3 = (-1.0 / a_r) * part2

    dhi_reflected = math.e ** part3

    return dhi_reflected


def current_milli_time():
    return round(time.time() * 1000)