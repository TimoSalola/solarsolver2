# coordinates
latitude = 60.204
longitude = 24.961

# panel angles
tilt = 15
azimuth = 135

module_elevation = 8 # 8 meters

# "Europe/Helsinki" should take summer/winter time into account, "GTM" is another useful timezone
timezone = "UTC"

# data resolution, how many minutes between measurements
data_resolution = 15

# ground albedo near solar panels, 0.25 is PVlib default. Has to be in range [0,1], typical values [0.1, 0.4]
# grass is 0.25, snow 0.8, worn asphalt 0.12. These values are from wikipedia https://en.wikipedia.org/wiki/Albedo
albedo = 0.151

# panel reflectance constant
reflectance_constant = 0.159

# rated installation power in kW, PV output at standard testing conditions
rated_power = 21