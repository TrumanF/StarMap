from SVG import SVG
from Star import Star
from StarManager import StarManager
from SolarSystemObject import SSO
import math
import numpy as np
import pandas as pd
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
OBS_TIME = "21:00:00"
OBS_DATE = "2023-02-10"
OBS_LOC = EarthLocation(lat=OBS_LAT, lon=OBS_LONG, height=100*u.m)
utcoffset = -8*u.hour
OBS_TIME_AP = Time(f'{OBS_DATE}T{OBS_TIME}') - utcoffset
aa = AltAz(location=OBS_LOC, obstime=OBS_TIME_AP)
STAR_NUM = 1500

# TODO: Use StarManager effectively :)
# TODO: Revisit normalization function for magnitude -> drawing size
# TODO: Add various legends to show magnitude scale, compass directions, labels for planets and sun/moon
# TODO: Constellation lines
# TODO: Constellation boxes/sections
# TODO: Ecliptic path
# TODO: Get color data for stars and lightly color each star as they're plotted
# TODO: Load an observing plan and draw connections between those stars with redline
# TODO: Be able to generate sections of sky
# TODO: Add SVG radial gradient


def spherical_to_cartesian(r, theta, phi):
    return r * math.cos(phi) * math.sin(theta), r * math.sin(phi) * math.sin(theta), r * math.cos(theta)


def polar_to_cartesian(r, theta):
    return r*math.cos(theta), r*math.sin(theta)


def plot_stars(chartSVG):
    # plot stars from .csv
    star_manager = StarManager((MAIN_CIRCLE_R, MAIN_CIRCLE_CX, MAIN_CIRCLE_CY), (OBS_LOC, OBS_TIME_AP), chartSVG)

    star_df = pd.read_csv('stars_labels.csv', keep_default_na=False)
    for ind in star_df.index[:STAR_NUM * 2]:
        temp_star = Star(star_df['ra'][ind], star_df['dec'][ind], star_df['mag'][ind], star_df['proper'][ind])
        star_manager.add_star(temp_star)
    # # find lowest and highest magnitude in list to normalize with
    # # TODO: only grab stars that can be plotted, i.e. alt > 0 in this frame
    # stars = star_manager.get_stars(STAR_NUM)
    # min_mag, max_mag = star_manager.get_mag_info()
    # labels = 0
    # for star in stars:
    #     labels += 1
    #     star.plot(chart, (MAIN_CIRCLE_R, MAIN_CIRCLE_CX, MAIN_CIRCLE_CY), (min_mag, max_mag), aa,
    #                    (True if labels < 25 else False))
    # print(star_manager)
    star_manager.plot_stars()


def plot_planets(chartSVG):
    jup = SSO('jupiter', aa, color='yellow')
    jup.plot(chartSVG, (MAIN_CIRCLE_R, MAIN_CIRCLE_CX, MAIN_CIRCLE_CY), 5, True)
    sat = SSO('saturn', aa, color='blue')
    sat.plot(chartSVG, (MAIN_CIRCLE_R, MAIN_CIRCLE_CX, MAIN_CIRCLE_CY), 5, True)
    mars = SSO('mars', aa, color='red')
    mars.plot(chartSVG, (MAIN_CIRCLE_R, MAIN_CIRCLE_CX, MAIN_CIRCLE_CY), 5, True)
    venus = SSO('venus', aa, color='green')
    venus.plot(chartSVG, (MAIN_CIRCLE_R, MAIN_CIRCLE_CX, MAIN_CIRCLE_CY), 5, True)
    sun = SSO('sun', aa, color='yellow')
    sun.plot(chartSVG, (MAIN_CIRCLE_R, MAIN_CIRCLE_CX, MAIN_CIRCLE_CY), 10, True)
    # plot some shit


def main():
    chartSVG = SVG(CANVAS_Y, CANVAS_X)
    chartSVG.circle(MAIN_CIRCLE_CX, MAIN_CIRCLE_CY, MAIN_CIRCLE_R, "white", width=5, fill=False)
    # print compass directions
    chartSVG.text(MAIN_CIRCLE_CX, MAIN_CIRCLE_CY + MAIN_CIRCLE_R, "N", size=50, color="white", dx=-15, dy=20)
    chartSVG.text(MAIN_CIRCLE_CX, MAIN_CIRCLE_CY - MAIN_CIRCLE_R, "S", size=50, color="white", dx=-15, dy=-50)
    chartSVG.text(MAIN_CIRCLE_CX + MAIN_CIRCLE_R, MAIN_CIRCLE_CY, "W", size=50, color="white", dx=15, dy=-15)
    chartSVG.text(MAIN_CIRCLE_CX - MAIN_CIRCLE_R, MAIN_CIRCLE_CY, "E", size=50, color="white", dx=-45, dy=-15)

    # consider changing circle center to "50%" if want to scale with canvas size, for now, OK

    # draw RA line markings at every hour
    ra_line_angles = np.linspace(0, 2*math.pi, 25)  # 25 segments, so we can ignore the redundant 0 and 2pi
    for angle in ra_line_angles[:-1]:
        x2, y2 = polar_to_cartesian(MAIN_CIRCLE_R, angle)
        chartSVG.line(MAIN_CIRCLE_CX, MAIN_CIRCLE_CY, x2 + MAIN_CIRCLE_CX, y2 + MAIN_CIRCLE_CY, color="white", width=1, opacity=1)

    # draw dec_lines at 22.5, 45, 67.5 degrees
    dec_lines = np.linspace(MAIN_CIRCLE_R, 0, 5)
    for radius in dec_lines[1:-1]:
        chartSVG.circle(MAIN_CIRCLE_CX, MAIN_CIRCLE_CY, radius, "white", width=1, fill=False)

    # plot stars
    plot_stars(chartSVG)

    # plot planets
    plot_planets(chartSVG)

    # Export to .svg
    chartSVG.export("StarChart.svg")


if __name__ == "__main__":
    main()
