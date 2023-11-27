import math

import matplotlib
import pandas
import xarray

import config

############################
#   FUNCTIONS FOR LOADING DATA
#   USE FIRST 3 FUNCTIONS, HELSINKI AND KUOPIO FMI CONTAIN HIGH QUALITY DATA
#   OTHER __FUNCTIONS ARE HELPERS, INTENDED FOR INTERNAL USE
############################


# these variables are used to store which days were read from csv, which were accepted and which were discarded
# can be read with solar_power_data_loader.all_days_in_dataset_df etc, useful for plotting and "data quality" tests
all_days_in_dataset_df = None
discarded_days_df = None
accepted_days_df = None


def get_fmi_helsinki_data_as_xarray():
    # filepath
    path = "fmi-helsinki-2021.csv"
    return __load_csv_as_xa(path)


def get_fmi_kuopio_data_as_xarray():
    # filepath
    path = "fmi-kuopio-2021.csv"
    return __load_csv_as_xa(path)


def get_oomi_laanila_oulu():
    path = "laanilan-koulu-oulu-2022.csv"
    data = __load_oomi_csv_as_xa(path)
    return data


def print_last_loaded_data_visual():
    """
    Creates a plot which shows the days within last loaded dataset, days which were discarded and days which were
    accepted
    :return: None
    """

    matplotlib.rcParams.update({'font.size': 13})
    matplotlib.pyplot.rcParams.update({
        "text.usetex": True
    })

    print(
        "Read " + str(len(all_days_in_dataset_df)) + " from datafile. Out of these " + str(len(accepted_days_df)) + "("
        + "%.2f" % round(100 * len(accepted_days_df) / len(all_days_in_dataset_df), 2) + "%) were good.")

    # plotting eventplot good days part
    for year_n in accepted_days_df["year"].unique():
        good_year_y = accepted_days_df.where(accepted_days_df["year"] == year_n)
        good_year_y = good_year_y.dropna()
        matplotlib.pyplot.eventplot(good_year_y["day"].values, lineoffsets=year_n, color=config.ORANGE)

    # plotting eventplot discarded days part
    for year_n in discarded_days_df["year"].unique():
        bad_days_y = discarded_days_df.where(discarded_days_df["year"] == year_n)
        bad_days_y = bad_days_y.dropna()
        matplotlib.pyplot.eventplot(bad_days_y["day"].values, lineoffsets=year_n, color="dimgrey")

    matplotlib.pyplot.xlabel("Day")
    matplotlib.pyplot.ylabel("Year")
    matplotlib.pyplot.title("Data quality")
    # matplotlib.pyplot.legend(["Accepted days", "Discarded days"])

    orange_patch = matplotlib.patches.Patch(color=config.ORANGE, label='Accepted days')
    grey_patch = matplotlib.patches.Patch(color="grey", label='Discarded days')
    white_patch = matplotlib.patches.Patch(color="white", label='Missing from dataset')
    matplotlib.pyplot.legend(handles=[orange_patch, grey_patch, white_patch])

    # max_year = max(all_days["year"].values)
    # min_year = min(all_days["year"].values)

    matplotlib.pyplot.ylim(min(all_days_in_dataset_df.year.values) - 0.5, max(all_days_in_dataset_df.year.values) + 0.5)
    matplotlib.pyplot.xlim(0, 365)
    matplotlib.pyplot.show()


def __load_oomi_csv_as_xa(csv_filename):
    """
    :param csv_filename: Name of csv file
    :return: xarray containing power generation data
    """

    """
    Function for processing another type of solar CSV files
    Files following this structure will not be included in the project
    In this format, power measurements are given every 10 minutes and in KWh -format
    This function transforms KWh per 10 min to W per s 
    """

    # expecting power to be in kwh over 10min, so 10 min to 60min = times 6
    # kwh to wh = 1000
    # 6000

    print("Loading oomidata from file " + str(csv_filename))
    data = pandas.read_csv(
        csv_filename,
        sep=";",  # ; normal separator
        skiprows=2,  # first 2 contain names
        names=["date", "power", "empty"],  # "data;data;empty"
        # nrows=10000000,
        encoding='unicode_escape',  # removes an unicode decoder error
        skipfooter=6,  # last 6 rows have averages and other data
        engine="python",  # removes a warning from console
        decimal=","  # seems to use 0,543 for power values
    )

    # loading dates and converting to datetime
    dates = data["date"]
    data["date"] = pandas.to_datetime(dates)

    # transforming kwh per 10min to w
    data["power"] = data["power"] * 6000  # for 10min kwh to w

    filtered_dataframe = pandas.DataFrame(data, columns=["date", "power"])

    minute_format_dataframe = __minute_format(filtered_dataframe)

    indexed_dataframe = minute_format_dataframe.set_index(["year", "day", "minute"])

    indexed_dataframe = indexed_dataframe[~indexed_dataframe.index.duplicated()]
    # print(indexed_dataframe)

    xa = indexed_dataframe.to_xarray()
    # print(xa)

    return xa


def __load_csv_as_xa(csv_filename):
    """
    WARNING, THIS REQUIRES THE CSV FILE TO FOLLOW SAME PATTERN AS FMI HELSINKI AND FMI KUOPIO
    :param csv_filename:
    :return:
    """

    """
    FMI data file pattern
    prod_time, pv_inv_out, pv_inv_in, pv_str_1, pv_str_2
    2015-08-26 03:34:00
    2015-08-26 03:35:00
    2015-08-26 03:36:00
    """

    print("Loading data from " + csv_filename)

    # importing data
    data = pandas.read_csv(
        csv_filename,
        sep=";",
        skiprows=16,
        names=["date", "output to grid", "power", "PV1", "PV2"],
        nrows=10000000
    )

    # dropping nan here might not be needed
    data = data.dropna()

    # modifying datetime field type to datetime.
    data["date"] = pandas.to_datetime(data["date"])

    # picking out the important fields of date and power from the dataframe
    filtered_dataframe = pandas.DataFrame(data, columns=["date", "power"])

    # changing format to our year, day minute, power -format. This splits the date to 3 fields
    df_minutes = __minute_format(filtered_dataframe)

    # naming the new 3 index columns
    df_minutes = df_minutes.set_index(["year", "day", "minute"])

    # printing how much data came out
    print("Read " + str(len(df_minutes)) + " rows.")

    # there should be some missing values, starting by dropping nans
    df_minutes = df_minutes.where(df_minutes.power > 0)
    df_minutes = df_minutes.dropna(how="any")  # any should remove values when year, day, minute or power are nan

    # interpolating nan values
    df_minutes = __fill_missing_values_df(df_minutes)
    # above adds nans for some reason? They have to be removed again

    # removing new nans
    df_minutes = df_minutes.dropna()

    # transforming dataframe to xarray
    xa = df_minutes.to_xarray()

    return xa


def __fill_missing_values_df(df):
    print("\tFilling missing values in df")

    '''
    This function is not especially pretty. 
    Dicts are used to iterate through the data and missing minutes are linearly approximated
    '''

    # creating a dict where year maps to a list of days for that year in dataset
    # should contain 2016 to [1, 2,3,3,4, ... 365], 2017 to [1,2...]
    year_to_day_list_dict = dict()

    # filling the year to day list dict
    for index_tuple in df.index.values:
        year = index_tuple[0]
        day = index_tuple[1]
        if year in year_to_day_list_dict:
            day_list = year_to_day_list_dict.get(year)
            if day_list[len(day_list) - 1] != day:
                day_list.append(day)
                year_to_day_list_dict[year] = day_list
        else:
            year_to_day_list_dict[year] = [day]

    full_set_of_years = []

    # dataframe creation lists
    all_days_in_dataset_n = []  # contains every single day
    all_years_in_dataset_n = []  # contains every single year
    good_days_in_dataset_n = []  # contains only good days
    good_years_in_dataset_n = []  # contains only good years
    bad_days_in_dataset_n = []  # contains discarded days
    bad_years_in_dataset_n = []  # contains discarded years

    # iterating through the dict where key = year, value = days of that year
    for year_n in year_to_day_list_dict.keys():

        # using the year key to slice the dataframe so that we get only that specific year
        df_of_year = df.xs(year_n, level=0)

        # list of every single day corresponding to this specific year
        year_days = year_to_day_list_dict[year_n]

        # list of days from this year which were OK, day numbers
        good_days_this_year = []

        # list of days from which year which were OK, dataframes
        days_without_missing_minutes = []

        # Looping through each day in year_days
        for day_n in year_days:
            # slicing the specific day from year long dataframe
            day = df_of_year.xs(day_n, level=0)

            all_days_in_dataset_n.append(day_n)
            all_years_in_dataset_n.append(year_n)
            # filling missing minutes from the day, returns None is day should be discarded
            day_without_missing_minutes = __fill_missing_minutes_discard_faulty(day)



            # got a good year
            if day_without_missing_minutes is not None:
                good_days_in_dataset_n.append(day_n)
                good_years_in_dataset_n.append(year_n)
                good_days_this_year.append(day_n)
                days_without_missing_minutes.append(day_without_missing_minutes)
            else:
                # got none, bad day
                bad_days_in_dataset_n.append(day_n)
                bad_years_in_dataset_n.append(year_n)

            # adding the day without missing minutes to a list of multiple days without missing minutes

        # merging the lists of days together to create a full year
        year_df = pandas.concat(days_without_missing_minutes, keys=good_days_this_year, names=["day", "minute"])
        # adding this year_df containing days without missing minutes to a list of processed years
        full_set_of_years.append(year_df)

    # merging processed years together, this final df should not be missing any minutes
    output_xa = pandas.concat(full_set_of_years, keys=year_to_day_list_dict.keys(), names=["year", "day", "minute"])
    # step above adds nans
    # print(output_xa)
    # print(type(output_xa))
    output_xa = output_xa.dropna(axis="columns", how="any")
    print("\tMissed values are now filled")

    # updating public dataframes which contain accepted dates
    global all_days_in_dataset_df
    all_days_in_dataset_df = pandas.DataFrame(list(zip(all_years_in_dataset_n, all_days_in_dataset_n)),
                                              columns=["year", "day"])
    global discarded_days_df
    discarded_days_df = pandas.DataFrame(list(zip(bad_years_in_dataset_n, bad_days_in_dataset_n)),
                                         columns=["year", "day"])
    global accepted_days_df
    accepted_days_df = pandas.DataFrame(list(zip(good_years_in_dataset_n, good_days_in_dataset_n)),
                                        columns=["year", "day"])

    return output_xa


def __fill_missing_minutes_discard_faulty(day):
    """
    V2 of function below
    Linear interpolation of missing minutes method
    :param day: pandas dataframe containing one day of data
    :return:
    """

    """
    Dataframe structure:
            power
    minute       
    296      14.0
    297      15.0
    298      25.0
    299      42.4
    300      40.1
    """

    """
    Possible cases,
    1. Too few or too many measurements, skip day
    2. Good day pattern but too few measurements, ____XxX__XXXXX____, skip day
    3. Good day and good amount of measurements, ____XXXX_XXXXXX____, interpolate and return
    4. Harder day pattern, both skipping and reparing are possibilities, skip for now
    """

    # checking measurement count
    min_measurement_count = 400
    max_measurement_count = 1200

    # too many or too few values within the day, discarding day
    if len(day) < min_measurement_count or len(day) > max_measurement_count:
        # print("Faulty day. Too few or too many power measurements")
        return None

    # checking if first and last measurements are within reasonable margin from end points

    first_minute = min(day.index)
    last_minute = max(day.index)

    if first_minute > 5 and last_minute < 1435:
        # ____xxxxx_____
        # easy case to handle

        window_size = last_minute - first_minute
        measurements_in_window = len(day)

        # if less than 99% of values are filled within window, discard day
        if measurements_in_window / window_size < 0.95:
            # print("Faulty day. More than 10% of measurements are missing.")
            return None

        # some values might be missing but day is a simple _____xxxxxx_xxx___
        missing_minutes = []
        missing_values = []

        for i in range(first_minute, last_minute):
            if i not in day.index:
                missing_minutes.append(i)
                missing_values.append(float("nan"))

        # creating a df from missing values and merging with known minutes
        missing_dict = {"minute": missing_minutes, "power": missing_values}
        df_missing_values = pandas.DataFrame.from_dict(missing_dict)
        df_missing_values = df_missing_values.set_index("minute")

        if day is None:
            return None

        if df_missing_values is None:
            return None

        if len(df_missing_values) == 0:
            return None

        full_day = pandas.concat([day, df_missing_values])  # TODO THIS CAUSES ERRORS WHEN EMPTY INPUTS
        full_day = full_day.sort_index()

        # interpolating nan values, resulting day should be usable
        full_day = full_day.interpolate(method="linear")

        # this loop check if interpolation worked, should never print exceptions but keeping this here just in case
        interpolated_powers = full_day.power.values
        for i in range(len(interpolated_powers)):
            if math.isnan(interpolated_powers[i]):
                raise Exception("Nan removal did not work in solar_power_data_loader function")

        return full_day

    # returning none if none of the cases applied, or if case 4 applies
    return None


def __fill_missing_minute_values_within_given_day(day):
    """
    TODO: LEGACY FUNCTION; SHOULD NOT BE USED
    Linear interpolation of missing minutes method
    :param day: pandas dataframe containing one day of data
    :return:
    """

    """
        Dataframe structure:
                power
        minute       
        296      14.0
        297      15.0
        298      25.0
        299      42.4
        300      40.1
    """

    first_minute = min(day.index)
    last_minute = max(day.index)

    missing_minutes = []
    missing_values = []

    # determines if trailing or leading values should be added
    fill_before_after = False

    for i in range(1440):
        if fill_before_after:
            if i < first_minute or i > last_minute:
                missing_minutes.append(i)
                missing_values.append(0)
            elif i not in day.index:
                missing_minutes.append(i)
                missing_values.append(float("nan"))
        else:
            if first_minute <= i <= last_minute and i not in day.index:
                missing_minutes.append(i)
                missing_values.append(float("nan"))

    missing_dict = {"minute": missing_minutes, "power": missing_values}
    df_missing_values = pandas.DataFrame.from_dict(missing_dict)
    df_missing_values = df_missing_values.set_index("minute")
    full1440day = pandas.concat([day, df_missing_values])
    full1440day = full1440day.sort_index()

    # INTERPOLATION HAPPENS HERE, interpolation is done twice, once from both different directions as the interpolation
    # method does not seem to be direction invariant. Using two interpolations seemed to fix the is
    full1440day = full1440day.interpolate(method="linear")
    full1440day = full1440day.reindex(index=full1440day.index[::-1])
    full1440day = full1440day.interpolate(method="linear")
    full1440day = full1440day.reindex(index=full1440day.index[::-1])

    return full1440day


def __minute_format(dataframe):
    """
    :param dataframe: datetime - power dataframe
    :return: year - day - minute - power dataframe
    """
    print("*Reformatting dataframe to [Year, Day, Minute, Power] -format")

    output = pandas.DataFrame.copy(dataframe, deep=True)

    output["minute"] = output["date"].dt.hour * 60 + output["date"].dt.minute

    output["year"] = output["date"].dt.year
    output["day"] = output["date"].dt.strftime("%j").astype(int)

    output2 = pandas.DataFrame(output, columns=["year", "day", "minute", "power"])

    return output2
