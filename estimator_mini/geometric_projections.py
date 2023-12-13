"""
Irradiance transposition functions. Used for transforming different solar irradiance components to panel
projected irradiance components.

https://www.campbellsci.ca/blog/albedo-resource-assessment

Terminology:
POA: Plane of array irradiance, the total amount of radiation which reaches the panel surface at a given time. This is
the sum of poa projected dhi, dni and ghi.
POA = "dhi_poa" + "dni_poa" + "ghi_poa"


GHI: Global horizontal irradiance
-- irradiance received by an area flat against the ground at a given location and at a given time.

DNI: Direct normal irradiance-irradiance received by a flat received pointing towards the Sun at given time,
given coordinates.

DHI/ DIF: Diffuse horizontal irradiance
— irradiance received from atmospheric scattering and clouds.

"""

import math
import time

import numpy
import pvlib.irradiance

import astronomical_calculations

def irradiance_df_to_poa_df(irradiance_df, latitude, longitude, tilt, azimuth):


    print("projecting irradiances to poa")
    print(latitude)
    print(longitude)
    print(tilt)
    print(azimuth)
    """
    :param azimuth:
    :param tilt:
    :param longitude:
    :param latitude:
    :param irradiance_df: Solar irradiance dataframe with ghi, dni and dhi components.
    :return: Dataframe with dni, ghi and dhi plane of array irradiance projections
    """







    # print("Translating irradiance_df columns [ghi, dni, dhi] to POA components.")

    # Note, the helper functions here and the df.apply() -structure should not be encouraged due to slower processing.
    # Vectorized operations should be used instead. However, this structure makes the projection functions easier to
    # understand and modify.

    # Vectorization has now been implemented, operation time went from 2 seconds to 6 ms
    # perez does not have zero checking, could prove to be an issue with real measurements of
    # dhi, dni, ghi

    # 3 projection functions

    # two dhi models, simple and perez
    def helper_dhi_poa_fast(dhi, tilt):
        return __project_dhi_to_panel_surface(dhi, tilt)

    def helper_dhi_poa_perez_fast(dhi, dni, timestamp):
        return __project_dhi_to_panel_surface_perez(timestamp, dhi, dni, tilt, azimuth, latitude, longitude)

    # 2 ghi functions for both cases, albedo in df and albedo not in df
    def helper_ghi_poa(df):
        return __project_ghi_to_panel_surface(df["ghi"], tilt)

    def helper_ghi_poa_dynamic_albedo(df):
        # using albedo from df if albedo column exists, otherwise uses config.albedo
        return __project_ghi_to_panel_surface(df["ghi"], df["albedo"])

    time1 = current_milli_time() #### 0 ms operation, super fast
    # adding 3 projected results to output df
    irradiance_df["dni_poa"] = helper_dhi_poa_fast(irradiance_df["dhi"], tilt )


    time2 = current_milli_time() ####  15 ms operation, fast
    # irradiance_df["dhi_poa"] = irradiance_df.apply(helper_dhi_poa_perez, axis=1)
    irradiance_df["dhi_poa"] = helper_dhi_poa_perez_fast(irradiance_df["dhi"], irradiance_df["dni"],
                                                         irradiance_df["time"])

    time3 = current_milli_time() #### 6 ms operation, super fast
    # 2 ghi  variants for dynamic and static albedo
    if "albedo" in irradiance_df.columns:
        irradiance_df["ghi_poa"] = irradiance_df.apply(helper_ghi_poa_dynamic_albedo, axis=1)
    else:
        irradiance_df["ghi_poa"] = irradiance_df.apply(helper_ghi_poa, axis=1)

    # adding the sum of projections to df as poa
    time4 = current_milli_time()



    irradiance_df["poa"] = irradiance_df["dhi_poa"] + irradiance_df["dni_poa"] + irradiance_df["ghi_poa"]
    time5 = current_milli_time()
    """
    print("DNI time " + str(time2 - time1) + " ms")
    print("DHI time " + str(time3 - time2) + " ms")
    print("GHI time " + str(time4 - time3) + " ms")
    print("total time " + str(time5 - time1) + " ms")
    """




    # print("POA transposition done.")
    return irradiance_df


"""
PROJECTION FUNCTIONS
4 functions for 3 components, 2 functions for DNI as either date or angle of incidence can be used for computing the 
same result.
"""


def __project_dni_to_panel_surface_using_time(dni, dt, latitude, longitude, tilt, azimuth):
    """
    Based on https://pvpmc.sandia.gov/modeling-steps/1-weather-design-inputs/plane-of-array-poa-irradiance
    /calculating-poa-irradiance/poa-beam/
    :param dni: Direct sunlight irradiance component in W
    :param dt: Time of simulation
    :return: Direct radiation per 1m² of solar panel surface
    """
    angle_of_incidence = astronomical_calculations.get_solar_angle_of_incidence(dt, latitude, longitude, tilt, azimuth)
    return abs(__project_dni_to_panel_surface_using_angle(dni, angle_of_incidence))


def __project_dni_to_panel_surface_using_angle(dni, angle_of_incidence):
    """
    :param dni: Direct sunlight irradiance component in W
    :param angle_of_incidence: angle between sunlight and solar panel normal, calculated by astronomical_calculations.py
    :return: Direct radiation hitting solar panel surface.
    """

    return dni * math.cos(numpy.radians(angle_of_incidence))


def __project_dhi_to_panel_surface(dhi, tilt):
    """
    Uses atmosphere scattered sunlight and solar panel angles to estimate how much of the scattered light is radiated
    towards solar panel surfaces.
    :param dhi: Atmosphere scattered irradiation.
    :return: Atmosphere scattered irradiation projected to solar panel surfaces.
    """
    return dhi * ((1.0 + math.cos(numpy.radians(tilt))) / 2.0)


def __project_dhi_to_panel_surface_perez(time, dhi, dni, tilt, azimuth, latitude, longitude):
    """
    Alternative dhi model, https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.irradiance.perez.html

    :param time:
    :param dhi:
    :param dni:
    :return:
    """

    # function parameters
    dni_extra = 1366.1  # From William Wandji, empirical value
    surface_tilt = tilt
    surface_azimuth = azimuth
    solar_azimuth, solar_zenith = astronomical_calculations.get_solar_azimuth_zenit(time, latitude, longitude)

    airmass = astronomical_calculations.get_air_mass(time, latitude, longitude)



    dhi_perez = pvlib.irradiance.perez(surface_tilt, surface_azimuth, dhi, dni, dni_extra, solar_zenith, solar_azimuth,
                                       airmass, return_components=False)

    print("time")
    print(time) # ok
    print("dhi:")
    print(dhi) # ok
    print("dni")
    print(dni)  # ok
    print("tilt:")
    print(tilt) # ok
    print("azimuth:")
    print(azimuth) # ok
    print("latitude:")
    print(latitude) # ok
    print("longitude:")
    print(longitude) # ok
    print("s_azimuth:")
    print(solar_azimuth) # ok
    print("s_zenith:")
    print(solar_zenith) # ok
    print("airmass:")
    print(airmass) # nan !
    print("dhi_perez:")
    print(dhi_perez)

    return dhi_perez


def __project_ghi_to_panel_surface(ghi, tilt, albedo=0.151):
    """
    Uses ground albedo and panel angles to estimate how much of the sunlight per 1m² of ground is radiated towards solar
    panel surfaces.
    :param ghi: Ground reflected solar irradiance.
    :return: Ground reflected solar irradiance hitting the solar panel surface.
    """
    step1 = (1.0 - math.cos(numpy.radians(tilt))) / 2
    step2 = ghi * albedo * step1
    return step2  # ghi * config.albedo * ((1.0 - math.cos(numpy.radians(config.tilt))) / 2.0)


def current_milli_time():
    return round(time.time() * 1000)