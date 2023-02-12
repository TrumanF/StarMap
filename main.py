from Chart import RadialChart
from astropy.coordinates import EarthLocation
from astropy.time import Time
from astropy import units as u
import datetime
# TODO: Make this information read from a .txt file or something, that way I can generate like 4 plots at a time
# input all location and time data
OBS_LAT = 37.716452
OBS_LONG = -122.496369
OBS_TIME = "18:00:00"
OBS_DATE = "2023-02-11"
OBS_LOC = EarthLocation(lat=OBS_LAT, lon=OBS_LONG, height=100*u.m)
utcoffset = -8*u.hour
OBS_TIME_AP = Time(f'{OBS_DATE}T{OBS_TIME}') - utcoffset


# TODO: Make some class that will generate the base template for me, that way it can have different skins easily
# TODO: Revisit normalization function for magnitude -> drawing size
# TODO: Add various legends to show magnitude scale, compass directions, labels for planets and sun/moon
# TODO: Constellation lines
# TODO: Constellation boxes/sections
# TODO: Ecliptic path
# TODO: Get color data for stars and lightly color each star as they're plotted
# TODO: Load an observing plan and draw connections between those stars with redline
# TODO: Be able to generate sections of sky
# TODO: Revise SVG gradient, it doesn't look that good
# TODO: PNG and GIF support
# TODO: Generate metadata in SVG that displays basic info about the plot, loc, time/date,
#  sorting filter used, number of stars, etc.
# TODO: Think about how I want to interact with Chart class, should I give star data immediately?
#  Or should I pass it in when I want to plot? What are the differences? Advantages?

def main():
    current_time = True
    if current_time:
        cur_time = Time("T".join(str(datetime.datetime.now()).split(" "))) - utcoffset
    size = 1500
    radChart1 = RadialChart((OBS_LOC, cur_time if current_time else OBS_TIME_AP), (size, size*1.2),
                            'Star CSV/hygdata_v3.csv')
    radChart1.plot(num_stars=2500, star_labels=20)
    radChart1.export("RadChart1.svg")


if __name__ == "__main__":
    main()
