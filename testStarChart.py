from SVG import SVG
from Star import Star
import math
import numpy as np
from astropy.coordinates import EarthLocation
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import AltAz

CANVAS_X = 1200 * 1.5
CANVAS_Y = 1000 * 1.5
MAIN_CIRCLE_R = (CANVAS_Y * .9)/2
MAIN_CIRCLE_CX = CANVAS_X/2
MAIN_CIRCLE_CY = CANVAS_Y/2

OBS_LAT = 37.716452
OBS_LONG = -122.496369
OBS_TIME = "12:00:00"
OBS_DATE = "2023-02-10"
OBS_LOC = EarthLocation(lat=OBS_LAT, lon=OBS_LONG, height=100*u.m)
utcoffset = -8*u.hour
OBS_TIME_AP = Time(f'{OBS_DATE}T{OBS_TIME}') + utcoffset
aa = AltAz(location=OBS_LOC, obstime=OBS_TIME_AP)
# TODO: Set position on earth so we can include southern hemisphere stars and all that
# TODO: Load an observing plan and draw connections between those stars with redline
# TODO: Optional labels in Star.py and display them on the map
# TODO: Constellation lines
# TODO: Constellation boxes/sections
# TODO: Revisit normalization function for magnitude -> drawing size
# TODO: Use pandas .csv reading for ease of use
# TODO: Maybe write code within Star that handles it's own plotting, i.e. negative ra value and add pi/2
# TODO: Add various legends to show magnitude scale, compass directions, labels for planets and sun/moon
# TODO: Get color data for stars and lightly color each star as they're plotted



def hms_to_deg(time):
    hour, minute, second = [int(t) for t in time.split(":")]
    return (hour * 15) + (minute * 15/60) + (second * 15/3600)


def spherical_to_cartesian(r, theta, phi):
    return r * math.cos(phi) * math.sin(theta), r * math.sin(phi) * math.sin(theta), r * math.cos(theta)


def polar_to_cartesian(r, theta):
    return r*math.cos(theta), r*math.sin(theta)


def main():
    test_chart = SVG(CANVAS_Y, CANVAS_X)
    test_chart.circle(MAIN_CIRCLE_CX, MAIN_CIRCLE_CY, MAIN_CIRCLE_R, "white", width=5, fill=False)
    # consider changing circle center to "50%" if want to scale with canvas size, for now, OK

    # draw RA line markings at every hour
    ra_line_angles = np.linspace(0, 2*math.pi, 25)  # 25 segments, so we can ignore the redundant 0 and 2pi
    for angle in ra_line_angles[:-1]:
        x2, y2 = polar_to_cartesian(MAIN_CIRCLE_R, angle)
        test_chart.line(MAIN_CIRCLE_CX, MAIN_CIRCLE_CY, x2 + MAIN_CIRCLE_CX, y2 + MAIN_CIRCLE_CY, color="white", width=1, opacity=1)

    # draw dec_lines at 22.5, 45, 67.5 degrees
    dec_lines = np.linspace(MAIN_CIRCLE_R, 0, 5)
    for radius in dec_lines[1:-1]:
        test_chart.circle(MAIN_CIRCLE_CX, MAIN_CIRCLE_CY, radius, "white", width=1, fill=False)

    # For true spherical projection
    # dec_lines = np.linspace(0, math.pi/2, 5)
    # print(dec_lines)
    # dec_lines_sphere = [spherical_to_cartesian(1, dec_line, 0) for dec_line in dec_lines]
    # dec_lines_projection = [coord[0] for coord in dec_lines_sphere]
    # for radius in dec_lines_projection[1:-1]:
    #     test.circle(MAIN_CIRCLE_CX, MAIN_CIRCLE_CY, radius*MAIN_CIRCLE_R, "white", width=1, fill=False)
    # print(dec_lines_projection)

    # plot stars from .csv
    stars = []
    stars_file = open("constellations/UrsaMajor.csv", "r", encoding='utf-8-sig')
    for line in stars_file.readlines():
        star_data = line.strip("\n").split(",")
        stars.append(Star(star_data[0], star_data[1], star_data[2]))

    # find lowest and highest magnitude in list to normalize with
    min_mag = min([star.mag for star in stars])
    max_mag = max([star.mag for star in stars])

    for star in stars:
        # if star.dec <= 0:
        #     continue
        star.plot(test_chart, (MAIN_CIRCLE_R, MAIN_CIRCLE_CX, MAIN_CIRCLE_CY), (0, 5), aa)




    # Export to .svg
    test_chart.export("testStarChart.svg")


if __name__ == "__main__":
    main()
