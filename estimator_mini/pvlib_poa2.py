import datetime

import pandas

import geometric_projections
import irradiance_estimator
import reflection_estimator

import time


def get_irradiance(year, day, lat, lon, tilt, azimuth):
    # year day
    """
    print("airmass test")
    now = datetime.now()
    b = datetime(2022, 6, 15, 21, 5)

    airmass = astronomical_calculations.get_air_mass(b, 65, 25)

    print("got airmass:")
    print(airmass)

    """

    time1 = current_milli_time()
    irrad_data = irradiance_estimator.get_irradiance_1_day(year, day, lat, lon)
    # no nan values this far, all good

    time2 = current_milli_time()
    projected_data = geometric_projections.irradiance_df_to_poa_df(irrad_data, lat, lon, tilt, azimuth)

    time3 = current_milli_time()


    reflected_data = reflection_estimator.add_reflection_corrected_poa_to_df(projected_data, lat, lon, tilt, azimuth)
    time4 = current_milli_time()
    output = reflected_data[["time", "poa_ref_cor"]]
    output = output.rename(columns={"poa_ref_cor": "poa"})

    # output = output.dropna()

    time5 = current_milli_time()


    print("## irradiance simulation time " + str(time2 - time1) + " ms")
    print("## projection simulation time " + str(time3 - time2) + " ms")
    print("## reflection simulation time " + str(time4 - time3) + " ms")
    print("## df parsing time " + str(time5 - time4) + " ms")
    print("## total time " + str(time5 - time1) + " ms")



    """
    irradiance simulation time 10 ms
    projection simulation time 5438 ms
    reflection simulation time 1978 ms
    df parsing time 1 ms
    total time 7427 ms
    """

    print(output)


    return output


def current_milli_time():
    return round(time.time() * 1000)

data = get_irradiance(2018, 150, 65, 25, 15, 135)

