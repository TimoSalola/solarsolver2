import math

import matplotlib.pyplot
import numpy
import config
import multiplier_matcher
import polarplotter
import pvlib_poa
import splitters


############################
#   FUNCTIONS FOR ESTIMATING PANEL ANGLES
#   USE find_best_multiplier_for_poa_to_match_single_day_using_integral FOR COMPUTING THE MULTIPLIER IF ANGLES ARE KNOWN
#   OTHER __FUNCTIONS ARE HELPERS, INTENDED FOR INTERNAL USE
############################


def test_single_pair_of_angles(day_xa, known_latitude, known_longitude, tilt, facing):
    """
    Tests a pair of angles against a day of measurements. Returns a fitness value, lower is better
    :param day_xa: xarrya containing one day of measurements
    :param known_latitude: latitude coordinate of installation in wgs84
    :param known_longitude: longitude coodrinate of installation in wgs84
    :param tilt: test tilt angle
    :param facing: test facing angle
    :return: fitness value, lower is better
    """

    # reading year and day from xa
    day_n = day_xa.day.values[0]
    year_n = day_xa.year.values[0]

    # creating initial poa
    poa_initial = pvlib_poa.get_irradiance(year_n, day_n, known_latitude, known_longitude, tilt, facing)

    # matching poa with single segment integral method
    multiplier = find_best_multiplier_for_poa_to_match_single_day_using_integral(day_xa, poa_initial)

    # matching multiplier
    poa_initial["POA"] = poa_initial["POA"] * multiplier

    # comparing multiplier matched with measurements for fitness value, lower is better
    fitness = get_measurement_to_poa_delta_cost(day_xa, poa_initial)

    return fitness


def take_poa_and_return_multiplied_poa_best_matching_measurements(xa_day, poa):
    """
    Takes measurements and simulation, returns simulation scaled to match measurements
    :param xa_day: xa containing one day of measurements
    :param poa: simulated plane of array irradiance curve
    :return: area matched poa curve
    """
    multiplier = find_best_multiplier_for_poa_to_match_single_day_using_integral(xa_day, poa)
    poa["POA"] = poa["POA"] * multiplier
    return poa


def get_measurement_to_poa_delta_cost(xa_day, poa):
    """
    Returns the delta between measurements and simualted values
    :param xa_day:
    :param poa:
    :return:
    """

    deltas, percents, minutes = __get_measurement_to_poa_delta(xa_day, poa)

    # print(percents)

    # percentual_cost = sum([abs(ele) for ele in percents]) / len(percents)

    # print(poa)
    # print(xa_day)

    abs_deltas = sum([abs(ele) for ele in deltas])

    return abs_deltas  # /len(deltas)


def find_best_multiplier_for_poa_to_match_single_day_using_integral(day_xa, poa):
    # Steps:
    # Find out common minutes
    # Calculate powers for xa and poa for those common minutes
    # calculate the ratio of these powers
    # use ratio as a multiplier
    # This should be similar to taking the integral over common points and comparing the areas

    # dropping na
    xa2 = day_xa.dropna(dim="minute")

    # getting area under measurements and the minutes that were used
    xa_minutes = xa2["minute"].values
    xa_powers = xa2["power"].values[0][0]
    sum_of_measured_powers = sum(xa_powers)

    # assuming that there are no gaps in the data
    first_minute = xa_minutes[0]
    last_minute = xa_minutes[len(xa_minutes) - 1]

    # print(" selecting interval " + str(first_minute) + " to " + str(last_minute))

    poa2 = poa.where(poa.minute >= first_minute)
    poa3 = poa2.where(poa.minute <= last_minute)
    poa4 = poa3.dropna()

    poa_sum_of_poa = sum(poa4["POA"])

    # this can be used as a multiplier to compute the required multiplier for the poa to match the measurements
    ratio = sum_of_measured_powers / poa_sum_of_poa

    return ratio


def get_multiplier_matched_poa(day_xa, latitude, longitude, tilt, azimuth):
    # day and year numbers from Xarray
    day_n = day_xa.day.values[0]
    year_n = day_xa.year.values[0]
    poa = pvlib_poa.get_irradiance(year_n, day_n, latitude, longitude, tilt, azimuth)
    multiplier = multiplier_matcher.get_estimated_multiplier_for_day(day_xa, poa)
    poa = pvlib_poa.get_irradiance_with_multiplier(year_n, latitude, longitude, day_n, tilt, azimuth, multiplier)

    return poa


def test_n_fibonacchi_sample_fitnesses_against_day(day_xa, samples, latitude, longitude):
    """
    Takes one good xa, known geolocation and sample count, returns tested angles and their fitnesses
    :param day_xa: cloud free xa
    :param samples: sample count, higher means more angle pairs will be tested
    :param latitude: known installation latitude coordinate
    :param longitude: known installation longitude coordinate
    :return: return [tilts(rad)], [azimuths(rad)], [fitnessess(decimal, lower better)]
    """

    # day and year numbers from Xarray
    day_n = day_xa.day.values[0]
    year_n = day_xa.year.values[0]

    # tilt and azimuth values on a fibonacci half sphere
    tilts_rad, azimuths_rad = get_fibonacci_distribution_tilts_azimuths(samples)

    delta = angular_distance_between_points(numpy.degrees(tilts_rad[0]), numpy.degrees(azimuths_rad[0]),
                                            numpy.degrees(tilts_rad[1]), numpy.degrees(azimuths_rad[1]))
    print("estimating grid density, assuming points are spread evenly there should be a point every " + str(
        round(delta, 4)) + " degrees")

    # tilt and azimuth values in degrees
    tilts_deg, azimuths_deg = [], []
    for i in range(len(tilts_rad)):
        tilts_deg.append((tilts_rad[i] / (2 * math.pi)) * 360)
        azimuths_deg.append((azimuths_rad[i] / (2 * math.pi)) * 360)

    # debugging messages
    # print("testing fitnessess at tilts:")
    # print(tilts_deg)
    # print("and azimuths")
    # print(azimuths_deg)

    # creating poa at tilt+azimuth and fitness
    fitnesses = []

    for i in range(len(tilts_deg)):
        tilt = tilts_deg[i]
        azimuth = azimuths_deg[i]
        fitness = test_single_pair_of_angles(day_xa, latitude, longitude, tilt, azimuth)
        fitnesses.append(fitness)

    return tilts_rad, azimuths_rad, fitnesses



def angle_intelligenlty_safe_one_day(day_of_measurements, latitude, longitude, start_point_count):

    print("Starting intelligent best fit search with " +str(start_point_count) +  " start points.")

    tilts = []
    azimuths = []
    fitnessess = []

    # generating lattice
    f_tilts, f_azimuths = get_fibonacci_distribution_tilts_azimuths(start_point_count)
    f_tilts = numpy.degrees(f_tilts).astype(int)
    f_azimuths= numpy.degrees(f_azimuths).astype(int)

    print("Tilts to test: " + str(f_tilts))
    print("Azimuths: " + str(f_azimuths))

    # testing where each lattice coordinate converges to
    for i in range(len(f_tilts)):
        f_tilt = f_tilts[i]
        f_azimuth = f_azimuths[i]
        tilt, azimuth, fitness = angle_intelligently_for_one_day(day_of_measurements, latitude, longitude,
                                                                    start_tilt=f_tilt,
                                                                    start_azimuth=f_azimuth)
        tilts.append(tilt)
        azimuths.append(azimuth)
        fitnessess.append(fitness)


    # solving best angles
    best_tilt, best_azimuth, best_fitness = get_best_fitness_out_of_results(tilts, azimuths, fitnessess)

    print(best_tilt)
    print(best_azimuth)
    print(best_fitness)







def angle_intelligently_for_one_day(day_of_measurements, latitude, longitude, start_tilt=45, start_azimuth=180, visualize=False):
    """
    Attempts to find best fit fast. Searches neighboring points and chooses point with best fitness, repeats and
    decreases search radius if nothing better can be found
    :param day_of_measurements: day to find fit for
    :param latitude: known latitude coordinate
    :param longitude: known longitude coordinate
    :param start_tilt: starting point for tilt angle, optional
    :param start_azimuth: starting point for azimuth coordinate, optional
    :param visualize: plot visualization or not, optional,
    :return: tilt, azimuth and fitness
    """


    ########################################################
    # starting point and point fitness, these values are always updated to contain best known fit
    center_tilt = start_tilt
    center_azimuth = start_azimuth
    center_fitness = math.inf  # note: lower is better

    # search distance, updating whenever needed
    search_distance = 25

    # init plot and mark starting point
    if visualize is True:
        polarplotter.init_polar_plot()
        # adding starting point
        polarplotter.add_scatter_point(center_tilt, center_azimuth, color=config.PURPLE, size=10, alpha=1)
        polarplotter.add_scatter_text(center_tilt, center_azimuth, "Start")

    # iteration counter
    iteration_counter = 0

    print("Starting parameter space search...")
    while True:
        iteration_counter += 1
        # new tilt and azimuth coordinates
        tilts, azimuths = __generate4_for_center_distance(center_tilt, center_azimuth, search_distance)

        found_better_fit = False

        # testing 4 nearby points
        for i in range(len(tilts)):
            # point p and point p fitness
            tilt_p = tilts[i]
            azimuth_p = azimuths[i]
            fitness_p = test_single_pair_of_angles(day_of_measurements, latitude, longitude, tilt_p, azimuth_p)

            # checking if fitness value on list was better than previous center
            if fitness_p < center_fitness:
                # fitness was better than previous center/previous best, updating
                found_better_fit = True
                center_tilt = tilt_p
                center_azimuth = azimuth_p
                center_fitness = fitness_p

        # adding new best fit to plot
        if visualize is True:
            polarplotter.add_scatter_point(center_tilt, center_azimuth, color="black", size=10)

        # decreasing search radius if better results could not be found
        if found_better_fit is False:
            if search_distance >= 25:
                search_distance = 10
            elif search_distance >= 10:
                search_distance = 5
            elif search_distance >= 5:
                search_distance = 1
            elif search_distance >= 1:
                search_distance = 0.5
            else:
                print("Search distance is low enough, stopping search")
                break

            print("could not find better results with previous search distance, new search distance:" + str(search_distance))

    # plotting best found fit
    if visualize is True:
        polarplotter.add_scatter_point(center_tilt, center_azimuth, color=config.ORANGE, size=10, alpha=1)
        polarplotter.add_scatter_text(center_tilt, center_azimuth, "Best fit")

    # search info print
    print("Finding best fit required " + str(iteration_counter) + " iterations.")
    print("Best fit was: " + str(center_tilt) + " tilt, " + str(center_azimuth) + " azimuth.")

    polarplotter.show_polar_plot()

    # returning best found fit
    return center_tilt, center_azimuth, center_fitness


def __generate4_for_center_distance(tilt, azimuth, distance):
    """
    Returns 2 lists with tilt and azimuth values which are near given point at distance d
    :param tilt:
    :param azimuth:
    :param distance:
    :return:
    """

    tilts = []
    azimuths = []

    """
          x1
          |
    x2----------x3
          |
          x4
    4 points
    """

    # point 1, tilt can reach over 90, sets limit
    azimuths.append(azimuth)
    if tilt + distance > 90:
        tilts.append(90)
    else:
        tilts.append(tilt + distance)

    # point 2, azimuth can reach over 360, sets overflow to azimuth+distance -360
    tilts.append(tilt)
    if azimuth + distance > 360:
        azimuths.append(azimuth + distance - 360)
    else:
        azimuths.append(azimuth + distance)

    # point 3 tilt can go below 0, sets tilt and reverses azimuth
    if tilt - distance < 0:
        tilts.append(-(tilt - distance))
        # tilt was handled, now for azimuth, should change phase by 180
        if azimuth > 180:
            azimuths.append(azimuth - 180)
        else:
            azimuths.append(azimuth + 180)
    else:
        tilts.append(tilt - distance)
        azimuths.append(azimuth)

    # point 4 azimuth can go below 0, set underflow to azimuth-distance + 360
    tilts.append(tilt)
    if azimuth - distance < 0:
        azimuths.append(azimuth - distance + 360)
    else:
        azimuths.append(azimuth - distance)

    return tilts, azimuths


############################
#   GLOBAL HELPERS
############################


def get_best_fitness_out_of_results(tilt_rads, azimuth_rads, fitnesses):
    """
    Returns tilt and azimuth values for lowest fitness value
    :param tilt_rads:
    :param azimuth_rads:
    :param fitnesses:
    :return: best_azimuth, best_tilt, best_fitness
    """

    best_azimuth = 0
    best_tilt = 0
    best_fit = math.inf
    for i in range(len(tilt_rads)):
        azimuth = azimuth_rads[i]
        tilt = tilt_rads[i]
        fitness = fitnesses[i]
        if fitness < best_fit:
            best_azimuth = azimuth
            best_tilt = tilt
            best_fit = fitness

    return best_tilt, best_azimuth, best_fit


def get_fibonacci_distribution_tilts_azimuths_near_coordinate(tilt, azimuth, samples_total, distance):
    """
    Unused function, generates local lattices
    Returns fibonacci lattice points which are closer than (distance) from (tilt) and (azimuth) in cartesian space
    :param tilt: Tilt angle in degrees
    :param azimuth: Azimuth angle in degrees
    :param samples_total: Samples in the complete fibonacci lattice, amount of returned points will be lower
    :param distance: max distance from tilt/azimuth
    :return: [tilts], [azimuths]
    """

    tilt_rad = numpy.radians(tilt)
    azimuth_rad = numpy.radians(azimuth)

    # xyz of tilt and azimuth
    x = math.cos(azimuth_rad) * math.sin(tilt_rad)
    y = math.sin(azimuth_rad) * math.sin(tilt_rad)
    z = math.cos(tilt_rad)

    print("xyz" + str(x) + " - " + str(y) + " " + str(z))

    # x y and z values for matplotlib test plotting
    xvals, yvals, zvals = [], [], []

    # actual tilt and azimuth values
    phis, thetas = [], []

    # doubling sample count as negative half of sphere is not needed
    # this should result in
    iterations = samples_total * 2
    for i in range(iterations):

        # using helper to get 5 values, x,y,z,phi,theta
        values = __get_fibonacci_sample(i, iterations)

        # if z is > 0, skip this loop iteration as bottom half of sphere is not needed
        if values[2] < 0:
            continue

        # xyz of fibonacci lattice points
        x_f = values[0]
        y_f = values[1]
        z_f = values[2]
        x_delta = x - x_f
        y_delta = y - y_f
        z_delta = z - z_f

        fibo_distance = math.sqrt(x_delta ** 2 + y_delta ** 2 + z_delta ** 2)

        print("fibonacci point distance: " + str(fibo_distance))

        if fibo_distance < distance:
            # point was closer to tilt and azimuth than distance, can be added to outputs
            # add values to lists
            xvals.append(values[0])
            yvals.append(values[1])
            zvals.append(values[2])
            phis.append(values[3])
            thetas.append(values[4])

    print(xvals)
    print(yvals)
    print(zvals)
    # test plotting
    fig = matplotlib.pyplot.figure()
    ax = fig.add_subplot(projection='3d')
    ax.scatter3D(xvals, yvals, zvals)
    matplotlib.pyplot.show()

    # returning tilt and azimuth values
    return phis, thetas


def get_fibonacci_distribution_tilts_azimuths(samples):
    """
    Returns tilt and azimuth values for the upper half of a fibonacci half sphere
    :param samples: approximate count for fibonacci half sphere points
    :return: [tilts(rad)], [azimuths(rad)], len(tilts) ~ samples
    """

    # x y and z values for matplotlib test plotting
    xvals, yvals, zvals = [], [], []

    # actual tilt and azimuth values
    phis, thetas = [], []

    # doubling sample count as negative half of sphere is not needed
    # this sould result in
    iterations = samples * 2
    for i in range(iterations):

        # using helper to get 5 values
        values = __get_fibonacci_sample(i, iterations)

        # if z is > 0, skip this loop iteration as bottom half of sphere is not needed
        if values[2] < 0:
            continue

        # add values to lists
        xvals.append(values[0])
        yvals.append(values[1])
        zvals.append(values[2])
        phis.append(values[3])
        thetas.append(values[4])

    # test plotting, shows the points in 3d space. Can be used for verification
    # fig = matplotlib.pyplot.figure()
    # ax = fig.add_subplot(projection='3d')
    # ax.scatter3D(xvals, yvals, zvals)
    # matplotlib.pyplot.show()

    # returning tilt and azimuth values
    return phis, thetas


############################
#   HELPERS BELOW, CALL ONLY FROM WITHIN THIS FILE
############################

def __get_fibonacci_sample(sample, sample_max):
    """
    :param sample: sample number when there are sample_max samples
    :param sample_max: highest sample number
    :return: x(-1,1), y(-1, 1), z(-1,1), tilt(rad) and azimuth(rad) values for a single point on a fibonacci sphere
    """

    # Code based on sample at https://medium.com/@vagnerseibert/distributing-points-on-a-sphere-6b593cc05b42

    k = sample + 0.5

    # degrees from top to bottom in radians
    phi = math.acos(1 - 2 * k / sample_max)
    # azimuth, goes super high superfast, this is why modulo is used to scale values down
    theta = math.pi * (1 + math.sqrt(5)) * k
    theta = theta % (math.pi * 2)

    x = math.cos(theta) * math.sin(phi)
    y = math.sin(theta) * math.sin(phi)
    z = math.cos(phi)

    return x, y, z, phi, theta


def angular_distance_between_points(tilt1, azimuth1, tilt2, azimuth2):
    """
    Calculates the angular distance in degrees between two points in angle space
    :param tilt1: point 1 tilt angle in degrees
    :param azimuth1: point 1 azimuth angle in degrees
    :param tilt2: point 2 tilt angle in degrees
    :param azimuth2: point 2 azimuth angle in degrees
    :return: sphere center angle between the two points
    """
    tilt1_rad = numpy.radians(tilt1)
    azimuth1_rad = numpy.radians(azimuth1)
    tilt2_rad = numpy.radians(tilt2)
    azimuth2_rad = numpy.radians(azimuth2)

    # print("Computing angular distance between two angle space points...")

    x1 = math.sin(tilt1_rad) * math.cos(azimuth1_rad)
    y1 = math.sin(tilt1_rad) * math.sin(azimuth1_rad)
    z1 = math.cos(tilt1_rad)

    # print("Point 1 x,y,z: " + str(round(x1, 2)) + " " + str(round(y1, 2)) + " " + str(round(z1,2)))

    x2 = math.sin(tilt2_rad) * math.cos(azimuth2_rad)
    y2 = math.sin(tilt2_rad) * math.sin(azimuth2_rad)
    z2 = math.cos(tilt2_rad)

    # print("Point 2 x,y,z: " + str(round(x2, 2)) + " " + str(round(y2, 2)) + " " + str(round(z2, 2)))

    euclidean_distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)

    center_angle = numpy.degrees(math.acos((2 - euclidean_distance ** 2) / 2))

    # print("Euclidean distance was: " + str(round(euclidean_distance, 4)) + " , angle delta: " +  str(round(center_angle, 4)) + " degrees")

    return center_angle


def __get_measurement_to_poa_delta(xa_day, poa):
    """
    Returns a list of deltas and percentual deltas which can be used for analytics
    :param xa_day: one day of measurements in xarray format
    :param poa: one day of measurements in numpy dataframe
    :return: list of deltas and list of percentual deltas
    """
    # removing the lowest values and nans
    xa_day = xa_day.where(xa_day.power >= 2)
    xa_day = xa_day.dropna(dim="minute")

    # loading poa minutes and powers
    poa_powers = poa["POA"].values
    poa_minutes = poa["minute"].values

    # loading xa minutes and powers
    xa_minutes = xa_day.minute.values
    xa_powers = xa_day.power.values[0][0]

    deltas = []  # absolute value of deltas
    percent_deltas = []  # percentual values of deltas, used for normalizing the errors as 5% at peak is supposed to
    # weight as much as 5% at bottom
    minutes = []  # contains minutes for which deltas were calculated for

    # print("computing delta between measurements and poa simulation")
    # print(xa_day)
    # print(poa)

    # TODO this loop here is likely to be the main cause for angle estimation being slow
    # Replace with vectorized operations?
    for i in range(len(xa_minutes)):
        xa_minute = xa_minutes[i]  # this is poa index
        xa_power = xa_powers[i]
        poa_power = poa_powers[xa_minute]

        delta = xa_power - poa_power

        # poa power may be 0, avoiding zero divisions here
        if poa_power > 1:
            percent_delta = (delta / poa_power) * 100
        else:
            percent_delta = None
        deltas.append(delta)
        percent_deltas.append(percent_delta)
        minutes.append(xa_minute)

    return deltas, percent_deltas, minutes
