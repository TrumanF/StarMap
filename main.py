from Chart import AzimuthalEQHemisphere, Stereographic
from astropy.coordinates import EarthLocation
from astropy.time import Time
from astropy import units as u
from Area import Area
from Area import ORION_AREA, URSA_MINOR_AREA, BIG_DIPPER_AREA
import datetime
import time

# TODO: Make this information read from a .txt file or something, that way I can generate like 4 plots at a time
# input all location and time data
OBS_LAT = 37.716452
OBS_LONG = -122.496369
OBS_TIME = "13:45:00"
OBS_DATE = "2023-02-19"
OBS_LOC = EarthLocation(lat=OBS_LAT, lon=OBS_LONG, height=100*u.m)
utcoffset = -8*u.hour
OBS_TIME_AP = Time(f'{OBS_DATE}T{OBS_TIME}') - utcoffset


# TODO: Make some class that will generate the base template for me, that way it can have different skins easily (?)
# TODO: Revisit normalization function for magnitude -> drawing size - I think maybe a gentle log scale would be best
# TODO: Add various legends to show magnitude scale, compass directions, labels for planets and sun/moon
# TODO: Constellation lines
# TODO: Constellation boxes/sections
# TODO: Ecliptic path
# TODO: Get color data for stars and lightly color each star as they're plotted
# TODO: Load an observing plan and draw connections between those stars with redline
# TODO: Revise SVG gradient, it doesn't look that good
# TODO: Check if text overlaps with other text and fix that, also check if items go outside main chart
# TODO: PNG and GIF support
# TODO: Revisit optimization, look at how often we do coordinate transformations
# TODO: Generate metadata in SVG that displays basic info about the plot, loc, time/date,
#  sorting filter used, number of stars, etc.
# TODO: Think about how I want to interact with Chart class, should I give star data immediately?
#  Or should I pass it in when I want to plot? What are the differences? Advantages?
# TODO: Add DSOs and plot their apparent sizes with ovals
# TODO: Add some sort of gradient on the star based on their variability?
# TODO: Generally revisit all places where a canvas size is determined and reevaluate
# TODO: Add PyGui support, will take a rework of where loaded stars are and lots of stuff
# TODO: Add Plate-Carree projection
# TODO: Be able to plot max magnitude numbers, i.e. no dimmer than 5
# TODO: Create area, where certain star is centered and FOV can be specified
# TODO: Make 3D view using distance (?)

# TODO: Figure out exactly why hemisphere can't be plotted
def main():
    current_time = True
    cur_time = Time("T".join(str(datetime.datetime.now()).split(" "))) - utcoffset
    size = 1500

    time1 = time.time()

    rad_chart1 = AzimuthalEQHemisphere((OBS_LOC, cur_time if current_time else OBS_TIME_AP), (size*1.2, size))
    rad_chart1.plot(num_stars=5000, star_labels=20, sort_filters=['mag'], reverse_flag=False)
    rad_chart1.export("RadChart1.svg")

    test_area = Area((8*15, 24*15), (-90, 0))
    # squareChart1 = Stereographic((OBS_LOC, cur_time if current_time else OBS_TIME_AP),
    #                              (size * 1.2, size), test_area, Orthographic=False)
    # squareChart1.plot(num_stars=2000, star_labels=30, sort_filters=['mag'], reverse_flag=False)
    # squareChart1.export("SquareChart1.svg")

    time2 = time.time()
    print(f'Entire script time: {time2-time1}')


if __name__ == "__main__":
    main()

