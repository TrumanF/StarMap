import math
import abc

from SVG import SVG
from Star import Star
from SolarSystemObject import SSO

import pandas as pd
import numpy as np
from astropy.time import Time
from astropy.coordinates import AltAz, EarthLocation, get_body
from astropy import units as u
import time

from multiprocessing import Pool


def polar_to_cartesian(r, theta):
    return r * math.cos(theta), r * math.sin(theta)


# NOTE: Add_star and add_sso are very similar, could be one function?
class Chart:
    def __init__(self, OBS_INFO, CANVAS_INFO, STAR_DATA):

        self.CANVAS_Y, self.CANVAS_X = CANVAS_INFO
        self.chartSVG = SVG(self.CANVAS_Y, self.CANVAS_X)  # NOTE: Consider making this abstract
        self.CHART_ELEMENT_OPACITY = .25
        self.CHART_ELEMENT_WIDTH = 2

        self.OBS_LOC, self.OBS_TIME = OBS_INFO  # astropy EarthLocation and Time objects
        self.AA = AltAz(location=self.OBS_LOC, obstime=self.OBS_TIME)  # AltAz frame from OBS_LOC and OBS_TIME

        self.star_list = []
        self.stars_above_horizon = []
        self.brightest_stars_list = []

        time1 = time.time()

        self.STAR_DATA = STAR_DATA  # path (str) to star.csv
        self.star_df = pd.read_csv(STAR_DATA, keep_default_na=False, nrows=20000)  # Note: change this 15000 to some variable

        # NOTE: Read more about pool.map_async()
        with Pool() as pool:
            result = pool.map_async(self.process_star, self.star_df.index)
            pool.close()
            pool.join()
        for star in result.get():
            self.add_star(star)

        time2 = time.time()
        print(f'Time: {time2-time1}')
        print(len(self.star_list))
        self.min_star_size = .5
        self.max_star_size = 7

        self.sso_list = []  # Note: probably needs a rename, something like 'active_sso_list' ?
        self.possible_sso = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']
        self.ssos_above_horizon = []

        for planet in self.possible_sso:
            self.add_sso(SSO(planet))

    def add_star(self, star):
        if star.alt > 0:
            self.stars_above_horizon.append(star)
        self.star_list.append(star)

    def process_star(self, i):
        new_star = Star(self.star_df['ra'][i], self.star_df['dec'][i], self.star_df['mag'][i], self.star_df['proper'][i])
        # Note: these lines could be moved to a general add_preprocess function, but not sure yet
        star_altaz_frame = new_star.coord.transform_to(self.AA)
        new_star.az = float(star_altaz_frame.az.to_string(unit=u.rad, decimal=True))
        new_star.alt = float(star_altaz_frame.alt.to_string(unit=u.deg, decimal=True))

        return new_star

    def brightest_stars(self):
        self.brightest_stars_list = sorted(self.stars_above_horizon, key=lambda star: star.mag)

    def sorted_stars(self, key, reverse_flag=False):
        # Note: Should this be stars_above_horizon? Or all stars?
        return sorted(self.stars_above_horizon, key=lambda star: getattr(star, key), reverse=reverse_flag)

    def add_sso(self, sso):
        sso.coord = get_body(sso.name, self.AA.obstime, self.AA.location)
        sso.ra = sso.coord.ra.to_string(unit=u.deg, decimal=True)
        sso.dec = sso.coord.dec.to_string(unit=u.deg, decimal=True)

        sso_altaz_frame = sso.coord.transform_to(self.AA)
        sso.az = float(sso_altaz_frame.az.to_string(unit=u.rad, decimal=True))
        sso.alt = float(sso_altaz_frame.alt.to_string(unit=u.deg, decimal=True))

        if sso.alt > 0:
            self.ssos_above_horizon.append(sso)

        self.sso_list.append(sso)

    @abc.abstractmethod
    def add_base_elements(self):
        pass

    @abc.abstractmethod
    def plot_preprocess_obj(self, cel_obj):
        pass

    @abc.abstractmethod
    def plot(self, stars=True, SSOs=True):
        pass


class RadialChart(Chart):
    def __init__(self, OBS_INFO, CANVAS_INFO, STAR_DATA):
        super().__init__(OBS_INFO, CANVAS_INFO, STAR_DATA)
        self.MAIN_CIRCLE_R = (self.CANVAS_Y * .9) / 2  # NOTE: Change multiplier to parameter
        self.SCALING_CONSTANT = self.MAIN_CIRCLE_R / 675.0  # Based on visual preference from other charts
        self.CHART_ELEMENT_WIDTH *= self.SCALING_CONSTANT
        self.MAIN_CIRCLE_CX = self.CANVAS_X / 2
        self.MAIN_CIRCLE_CY = self.CANVAS_Y / 2
        # call function to create base chart
        self.add_base_elements()

    def __repr__(self):
        return f'RadialChart | Stars loaded: {len(self.star_list)} | SSOs loaded :{len(self.sso_list)}'

    def add_base_elements(self):
        self.chartSVG.circle(self.MAIN_CIRCLE_CX, self.MAIN_CIRCLE_CY, self.MAIN_CIRCLE_R, "white", width=5*self.SCALING_CONSTANT, fill=False)
        # consider changing circle center to "50%" if I want to scale with canvas size, for now, OK
        # draw RA line markings at every hour
        ra_line_angles = np.linspace(0, 2 * math.pi, 25)  # 25 segments, so we can ignore the redundant 0 and 2pi
        for angle in ra_line_angles[:-1]:
            x2, y2 = polar_to_cartesian(self.MAIN_CIRCLE_R, angle)
            self.chartSVG.line(self.MAIN_CIRCLE_CX, self.MAIN_CIRCLE_CY, x2 + self.MAIN_CIRCLE_CX,
                               y2 + self.MAIN_CIRCLE_CY, "white", width=self.CHART_ELEMENT_WIDTH,
                               opacity=self.CHART_ELEMENT_OPACITY)

        # draw dec_lines at 22.5, 45, 67.5 degrees
        dec_lines = np.linspace(self.MAIN_CIRCLE_R, 0, 5)
        for radius in dec_lines[1:-1]:
            self.chartSVG.circle(self.MAIN_CIRCLE_CX, self.MAIN_CIRCLE_CY, radius, "white",
                                 width=self.CHART_ELEMENT_WIDTH, fill=False, opacity=self.CHART_ELEMENT_OPACITY)

        # print compass directions
        text_size = 50 * self.SCALING_CONSTANT
        self.chartSVG.text(self.MAIN_CIRCLE_CX, self.MAIN_CIRCLE_CY + self.MAIN_CIRCLE_R, "N", size=text_size,
                           color="white", dx=-15*self.SCALING_CONSTANT, dy=20*self.SCALING_CONSTANT)
        self.chartSVG.text(self.MAIN_CIRCLE_CX, self.MAIN_CIRCLE_CY - self.MAIN_CIRCLE_R, "S", size=text_size,
                           color="white", dx=-15*self.SCALING_CONSTANT, dy=-50*self.SCALING_CONSTANT)
        self.chartSVG.text(self.MAIN_CIRCLE_CX + self.MAIN_CIRCLE_R, self.MAIN_CIRCLE_CY, "W", size=text_size,
                           color="white", dx=15*self.SCALING_CONSTANT, dy=-15*self.SCALING_CONSTANT)
        self.chartSVG.text(self.MAIN_CIRCLE_CX - self.MAIN_CIRCLE_R, self.MAIN_CIRCLE_CY, "E", size=text_size,
                           color="white", dx=-45*self.SCALING_CONSTANT, dy=-15*self.SCALING_CONSTANT)

        # draw magnitude legend
        # self.chartSVG.rect(50, self.CANVAS_Y - 50, 250, 325, fill="none", stroke_width=3, rx=2)

    def plot_preprocess_obj(self, cel_obj):
        cel_obj.normalized_alt = -1 * (cel_obj.alt / 90 - 1)
        # stars with 90 should plot at center, stars with zero should be on edge, so normalize and reverse direction
        x, y = polar_to_cartesian((cel_obj.normalized_alt * self.MAIN_CIRCLE_R), -cel_obj.az + math.pi / 2)
        # -az because AZ increases to the east and add pi/2 to ensure north is up
        cel_obj.x, cel_obj.y = -x + self.MAIN_CIRCLE_CX, y + self.MAIN_CIRCLE_CY

    def plot(self, num_stars=500, SSOs=True, sort_filter='mag', reverse_flag=False, star_labels=None):
        if num_stars:
            self.plot_stars(num_stars, sort_filter, reverse_flag, star_labels)
        if SSOs:
            self.plot_ssos(SSOs)


    def plot_star(self, star, mag_info):
        self.plot_preprocess_obj(star)
        # Note: This works great, but if I wanted to plot again with different
        #  visual parameters, I'd have to re-preprocess, which doesn't need to happen since the xy
        #  coords would be the same
        min_mag, max_mag = mag_info
        # make line below its own function?
        star.size = self.max_star_size * (
                1 - (star.mag - min_mag) / (max_mag - min_mag)) + self.min_star_size
        star.size *= self.SCALING_CONSTANT
        self.chartSVG.circle(star.x, star.y, star.size, star.color, fill="url(#StarGradient1)", width=0)

    # TODO: Make better 'labels' flag, maybe can specify by filter which stars get labels
    #  Use a similar sorted() thing, to specify highest mag labs, ra, dec, etc... Random labels too
    # TODO: Change num_stars to be able to specify that you want all available stars to be plotted
    def plot_stars(self, num_stars, sort_filter=None, reverse_flag=False, labels=None):
        sorted_stars_to_plot = self.sorted_stars(sort_filter, reverse_flag)
        # NOTE: This can be made faster in some scenarios where sorted_stars already is sorted by mag
        sorted_stars_mag_sorted = [st.mag for st in sorted(sorted_stars_to_plot, key=lambda s: s.mag)]
        min_mag = min(sorted_stars_mag_sorted)
        max_mag = max(sorted_stars_mag_sorted)
        if num_stars > len(sorted_stars_to_plot):
            num_stars = len(sorted_stars_to_plot) - 1
            print(f"Number of stars requested is greater than available to plot, setting number to {num_stars}")
        for star in sorted_stars_to_plot[:num_stars]:
            self.plot_star(star, (min_mag, max_mag))
        if labels:
            for star in sorted_stars_to_plot[:num_stars][:labels]:
                self.chartSVG.text(star.x, star.y, star.name.capitalize(), color=star.color, dx=5 + star.size,
                                   size=15*self.SCALING_CONSTANT)

    def plot_sso(self, sso):
        self.plot_preprocess_obj(sso)
        sso.size *= self.SCALING_CONSTANT
        self.chartSVG.circle(sso.x, sso.y, sso.size, sso.color, fill=sso.color)

        if sso.label_print:
            self.chartSVG.text(sso.x, sso.y, sso.name.capitalize(), color=sso.color, dx=5 + sso.size,
                               size=15*self.SCALING_CONSTANT)

    # TODO: Revisit the 'plotting_list', code seems a little funky
    def plot_ssos(self, plotting_list=True):
        if type(plotting_list) is list:
            for sso in self.ssos_above_horizon:
                if sso.name in plotting_list:
                    self.plot_sso(sso)
        else:
            if plotting_list:  # this seems a little funky, but should work just fine
                for sso in self.ssos_above_horizon:
                    self.plot_sso(sso)

    def export(self, file_name):
        self.chartSVG.export(file_name)


class SquareChart(Chart):
    def __init__(self, OBS_INFO, CANVAS_INFO, STAR_DATA):
        super().__init__(OBS_INFO, CANVAS_INFO, STAR_DATA)
        # call function to create base chart
        self.add_base_elements()

    def add_base_elements(self):
        pass

    def plot_preprocess_obj(self, cel_obj):
        pass

    def plot(self, stars=True, SSOs=True):
        pass


def test():
    OBS_LAT = 37.716452
    OBS_LONG = -122.496369
    OBS_TIME = "13:00:00"
    OBS_DATE = "2023-02-11"
    OBS_LOC = EarthLocation(lat=OBS_LAT, lon=OBS_LONG, height=100 * u.m)
    utcoffset = -8 * u.hour
    OBS_TIME = Time(f'{OBS_DATE}T{OBS_TIME}') - utcoffset

    testRad = RadialChart((OBS_LOC, OBS_TIME), (1500, 1800), 'Star CSV/stars_labels.csv')
    print(testRad.sorted_stars('mag')[:500])


if __name__ == "__main__":
    test()
