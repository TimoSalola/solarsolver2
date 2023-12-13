from datetime import datetime


from pvlib import location
import pandas as pd

def get_irradiance_1_day(year, day, latitude, longitude):
    # creating site data required by pvlib poa
    site = location.Location(latitude, longitude, tz="UTC")

    # creating a pandas entity containing the times for which the irradiance is modeled for
    date = datetime.strptime(str(year) + "-" + str(day), "%Y-%j").strftime("%m-%d-%Y")

    times = pd.date_range(date,  # year + day for which the irradiance is calculated
                          freq="15min",  # take measurement every 60 minutes
                          periods=60 * 24 /15,  # how many measurements, 60 * 24 for 60 times per 24 hours = 1440
                          tz=site.tz)  # timezone

    # creating a clear sky and solar position entities
    clearsky = site.get_clearsky(times)

    # adds index as a separate time column, for some reason this is required as even a named index is not callable
    # with df[index_name] and df.index is not supported by function apply structures
    clearsky.insert(loc=0, column="time", value=clearsky.index)

    # returning clearsky irradiance df
    return clearsky