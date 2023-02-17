import math
import abc
import operator

from SVG import SVG
from Star import Star
from SolarSystemObject import SSO

import pandas as pd
import numpy as np
from astropy.time import Time
from astropy.coordinates import AltAz, EarthLocation, get_body
from astropy import units as u


from multiprocessing import Pool


def polar_to_cartesian(r, theta):
    return r * math.cos(theta), r * math.sin(theta)


# TODO: SquareChart doesn't actually need location, so take that out of the Chart class and move to RadialChart
# TODO: Rename RadialChart to HemisphereChart or AzimuthalEQ or something
# Note: Add_star and add_sso are very similar, could be one function?
class Chart:
    # Note: Read this shit
    # https://www.projectpluto.com/project.htm
    def __init__(self, OBS_INFO, CANVAS_INFO):

        self.CANVAS_X, self.CANVAS_Y = CANVAS_INFO
        self.CANVAS_CENTER = (self.CANVAS_X/2, self.CANVAS_Y/2)
        self.chartSVG = SVG(self.CANVAS_X, self.CANVAS_Y)  # NOTE: Consider making this abstract
        self.CHART_ELEMENT_OPACITY = .25
        self.CHART_ELEMENT_WIDTH = 2.5

        self.OBS_LOC, self.OBS_TIME = OBS_INFO  # astropy EarthLocation and Time objects
        self.AA = AltAz(location=self.OBS_LOC, obstime=self.OBS_TIME)  # AltAz frame from OBS_LOC and OBS_TIME

        self.star_df = pd.read_csv('Star CSV/hygdata_v3.csv', keep_default_na=False,
                                   nrows=5000)  # Note: change this magic number to some variable

        self.stars_above_horizon = []  # Note: This should exist only in RadialChart
        self.star_list = []

        # NOTE: Read more about pool.map_async()
        with Pool() as pool:
            result = pool.map_async(self.process_star, self.star_df.index)
            pool.close()
            pool.join()
        for star in result.get():
            self.add_star(star)

        self.min_star_size = 1
        self.max_star_size = 8

        self.sso_list = []  # Note: probably needs a rename, something like 'active_sso_list' ?
        self.possible_sso = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']
        self.ssos_above_horizon = []  # Note: This should exist only in RadialChart

        for planet in self.possible_sso:
            self.add_sso(SSO(planet))

    # Note: This function isn't abstract but is overriden depending on the needs of the child chart
    #  Maybe it should be?
    def add_star(self, star):
        # Accepts Star object and adds to main star_list
        self.star_list.append(star)

    def process_star(self, i) -> Star:
        # Processes star information from main star dataframe (star_df) and returns Star object
        new_star = Star(self.star_df['ra'][i], self.star_df['dec'][i], self.star_df['mag'][i], self.star_df['id'][i],
                        self.star_df['dist'][i], self.star_df['proper'][i], con=self.star_df['con'][i])
        star_altaz_frame = new_star.coord.transform_to(self.AA)
        new_star.az = float(star_altaz_frame.az.to_string(unit=u.rad, decimal=True))
        new_star.alt = float(star_altaz_frame.alt.to_string(unit=u.deg, decimal=True))

        return new_star

    # Note: This method is probably static, deal with that, or think about why it isn't
    def sort_stars(self, list_to_sort, keys, reverse_flag=False):
        # Note: Should this be stars_above_horizon? Or all stars?
        # Note: Sorted() sucks, can't tell it which key needs to be reversed, just deal with it for now
        temp = sorted(list_to_sort, key=operator.attrgetter(*keys), reverse=reverse_flag)

        return temp

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
    def plot(self, num_stars=500, SSOs=True):
        pass


class AzimuthalEQHemisphere(Chart):
    # Uses Azimuthal equidistant projection
    def __init__(self, OBS_INFO, CANVAS_INFO):
        super().__init__(OBS_INFO, CANVAS_INFO)
        self.MAIN_CIRCLE_R = (self.CANVAS_Y * .9) / 2  # Note: Change multiplier to parameter
        self.SCALING_CONSTANT = self.MAIN_CIRCLE_R / 675.0  # Based on visual preference from other charts
        self.CHART_ELEMENT_WIDTH = max(1, self.SCALING_CONSTANT * self.CHART_ELEMENT_WIDTH)
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
            x2, y2 = polar_to_cartesian(self.MAIN_CIRCLE_R, angle + math.pi/2)
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
    def add_star(self, star):
        # Accepts Star object and adds to main star_list
        if star.alt > 0:
            self.stars_above_horizon.append(star)

        self.star_list.append(star)

    def plot_preprocess_obj(self, cel_obj):
        cel_obj.normalized_alt = -1 * (cel_obj.alt / 90 - 1)
        # stars with 90 should plot at center, stars with zero should be on edge, so normalize and reverse direction
        x, y = polar_to_cartesian((cel_obj.normalized_alt * self.MAIN_CIRCLE_R), -cel_obj.az + math.pi / 2)
        # -az because AZ increases to the east and add pi/2 to ensure north is up
        cel_obj.x, cel_obj.y = -x + self.MAIN_CIRCLE_CX, y + self.MAIN_CIRCLE_CY

    def plot(self, num_stars=500, SSOs=True, sort_filters='mag', reverse_flag=False, star_labels=None):
        if num_stars:
            self.plot_stars(num_stars, sort_filters, reverse_flag, star_labels)
        if SSOs:
            self.plot_ssos(SSOs)

    def plot_star(self, star, mag_info):
        self.plot_preprocess_obj(star)
        # Note: This works great, but if I wanted to plot again with different
        #  visual parameters, I'd have to re-preprocess, which doesn't need to happen since the xy
        #  coords would be the same
        #  Although, I would have to call this function every time if I changed the main circle size
        min_mag, max_mag = mag_info
        # make line below its own function?
        star.size = self.max_star_size * (
                1 - (star.mag - min_mag) / (max_mag - min_mag)) + self.min_star_size
        star.size *= self.SCALING_CONSTANT
        self.chartSVG.circle(star.x, star.y, star.size, star.color, fill="url(#StarGradient1)", width=0)

    # TODO: Make better 'labels' flag, maybe can specify by filter which stars get labels
    #  Use a similar sorted() thing, to specify highest mag labs, ra, dec, etc... Random labels too
    # TODO: Change num_stars to be able to specify that you want all available stars to be plotted
    # Note: sort_filter could accept a sorted() key so that the filter could be highly customized \
    #  Same applies to labels, could be a sorted() key
    # TODO: Add functionality where filtered stars can be placed on all stars, but in different color
    # TODO: Ensure all sort filters come in lower_case()
    def plot_stars(self, num_stars, sort_filters=None, reverse_flag=False, labels=None):
        if type(sort_filters) is not list:
            sort_filters = [sort_filters.lower()]
        # Note: This affects the plotting size, moved [:num_stars] to for loop when plotting if want universal scale
        sorted_stars_to_plot = self.sort_stars(self.stars_above_horizon, sort_filters, reverse_flag)[:num_stars]
        # Note: This can be made faster in some scenarios where sorted_stars already is sorted by mag
        sorted_stars_mag_sorted = [st.mag for st in sorted(sorted_stars_to_plot, key=lambda s: s.mag)]
        min_mag = min(sorted_stars_mag_sorted)
        max_mag = max(sorted_stars_mag_sorted)
        # Check if requested number of stars is greater than amount available to be on plot
        if num_stars > len(sorted_stars_to_plot):
            num_stars = len(sorted_stars_to_plot) - 1
            print(f"Number of stars requested is greater than available to plot, setting number to {num_stars}")
        for star in sorted_stars_to_plot:
            self.plot_star(star, (min_mag, max_mag))
        if labels:
            for star in sorted_stars_to_plot[:num_stars][:labels]:
                self.chartSVG.text(star.x, star.y, star.name.capitalize() if star.name else star.id, color=star.color, dx=5 + star.size,
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


# TODO: Add SSO support for OrthographicArea
# Note: The constellations are graphing backwards right now... Can be fixed by returning -x in ra_dec_to_xy
class OrthographicArea(Chart):
    def __init__(self, OBS_INFO, CANVAS_INFO, area):
        super().__init__(OBS_INFO, CANVAS_INFO)
        self.area_center = area.center  # rads
        self.ra_center, self.dec_center = self.area_center  # rads
        self.RA_SCOPE = area.RA_SCOPE  # tuple, rads
        self.DEC_SCOPE = area.DEC_SCOPE  # tuple, rads
        self.RA_RANGE = area.RA_RANGE  # float, rads
        self.DEC_RANGE = area.DEC_RANGE  # float, rads

        self.MAX_X_SIZE = (self.CANVAS_X / 2) * .8
        self.MAX_Y_SIZE = (self.CANVAS_Y / 2) * .8
        self.BBOX = None
        self.SCALE = None
        self.set_scale()

        # call function to create base chart
        self.add_base_elements()

        self.stars_in_range = []
        self.find_stars_in_range()

        self.min_star_size = .75
        self.max_star_size = 10
        # divide the values by 2 since the plot is generated at 0,0 in center of canvas

    def find_stars_in_range(self):
        for star in self.star_list:
            if self.RA_SCOPE[0] < math.radians(star.ra) < self.RA_SCOPE[1] and self.DEC_SCOPE[0] < math.radians(star.dec) < self.DEC_SCOPE[1]:
                self.stars_in_range.append(star)

    # TODO: Instead of plotting a grid of RA/Dec lines, plot 4 of the nearest whole or near-whole multiples of RA/Dec
    def add_base_elements(self, bbox=True):
        ra_space = np.linspace(self.RA_SCOPE[0], self.RA_SCOPE[1], 100)
        dec_space = np.linspace(self.DEC_SCOPE[0], self.DEC_SCOPE[1], 100)

        ra_sample = np.linspace(self.RA_SCOPE[0], self.RA_SCOPE[1], 6)
        dec_sample = np.linspace(self.DEC_SCOPE[0], self.DEC_SCOPE[1], 6)
        # This code needs to be written, it kinda sucks, but it's partially because of SVG.curve()

        for i, dec_samp in enumerate(dec_sample):
            curve = []
            if i == 0 or i == len(ra_sample) - 1:
                width = 5
                stroke_opacity = 1
            else:
                width = 2
                stroke_opacity = .25
            for ra in ra_space:
                point = self.ra_dec_to_xy(ra, dec_samp)
                point = (point[0] * self.SCALE + self.CANVAS_CENTER[0], -point[1] * self.SCALE + self.CANVAS_CENTER[1])
                curve.append(point)
            self.chartSVG.curve(curve, width=width, stroke_opacity=stroke_opacity)
        for i, ra_samp in enumerate(ra_sample):
            curve = []
            if i == 0 or i == len(ra_sample) - 1:
                width = 5
                stroke_opacity = 1
            else:
                width = 2
                stroke_opacity = .25
            for dec in dec_space:
                point = self.ra_dec_to_xy(ra_samp, dec)
                point = (point[0] * self.SCALE + self.CANVAS_CENTER[0], -point[1] * self.SCALE + self.CANVAS_CENTER[1])
                curve.append(point)
            self.chartSVG.curve(curve, width=width, stroke_opacity=stroke_opacity)
        if bbox:
            self.chartSVG.rect(self.BBOX[0][0], self.BBOX[1][1], self.BBOX[1][0] - self.BBOX[0][0], self.BBOX[1][1] - self.BBOX[0][1], fill="None")

    def plot_preprocess_obj(self, cel_obj):
        cel_obj.x, cel_obj.y = self.ra_dec_to_xy(math.radians(cel_obj.ra), math.radians(cel_obj.dec))

    def plot(self, num_stars=500, SSOs=True, sort_filters='mag', reverse_flag=False, star_labels=None):
        if num_stars:
            self.plot_stars(num_stars, sort_filters, reverse_flag, star_labels)
        # if SSOs:
        #     self.plot_ssos(SSOs)

    def ra_dec_to_xy(self, ra, dec):
        # ra and dec input in radians
        delta_ra = ra - self.ra_center
        x = math.cos(dec) * math.sin(delta_ra)
        y = math.sin(dec) * math.cos(self.dec_center) - math.cos(dec) * math.cos(delta_ra) * math.sin(self.dec_center)
        # Note: Should I scale values here or later?
        return -x, y

    def plot_star(self, star, mag_info):
        self.plot_preprocess_obj(star)
        min_mag, max_mag = mag_info
        # make line below its own function?
        star.size = self.max_star_size * (
                1 - (star.mag - min_mag) / (max_mag - min_mag)) + self.min_star_size
        self.chartSVG.circle(star.x*self.SCALE + self.CANVAS_CENTER[0], star.y*self.SCALE + self.CANVAS_CENTER[1], star.size,
                             star.color, fill="url(#StarGradient1)", width=0)

    def plot_stars(self, num_stars, sort_filters=None, reverse_flag=False, labels=None):
        if type(sort_filters) is not list:
            sort_filters = [sort_filters.lower()]
        # Note: This affects the plotting size, moved [:num_stars] to for loop when plotting if want universal scale
        sorted_stars_to_plot = self.sort_stars(self.stars_in_range, sort_filters, reverse_flag)[:num_stars]
        # Note: This can be made faster in some scenarios where sorted_stars already is sorted by mag
        sorted_stars_mag_sorted = [st.mag for st in sorted(sorted_stars_to_plot, key=lambda s: s.mag)]
        min_mag = min(sorted_stars_mag_sorted)
        max_mag = max(sorted_stars_mag_sorted)
        # Check if requested number of stars is greater than amount available to be on plot
        if num_stars > len(sorted_stars_to_plot):
            num_stars = len(sorted_stars_to_plot) - 1
            print(f"Number of stars requested is greater than available to plot, setting number to {num_stars}")
        for star in sorted_stars_to_plot:
            self.plot_star(star, (min_mag, max_mag))

        # Note: Come back to labels
        # if labels:
        #     for star in sorted_stars_to_plot[:num_stars][:labels]:
        #         self.chartSVG.text(star.x, star.y, star.name.capitalize() if star.name else star.id, color=star.color, dx=5 + star.size,
        #                            size=15*self.SCALING_CONSTANT)

    def set_scale(self):
        # Note: the 4 lines below are FLAWED
        lower_coord = self.ra_dec_to_xy(self.RA_SCOPE[0], self.DEC_SCOPE[0])
        upper_coord = self.ra_dec_to_xy(self.RA_SCOPE[1], self.DEC_SCOPE[1])

        scales = ((self.MAX_X_SIZE / abs(lower_coord[0])), (self.MAX_Y_SIZE / abs(lower_coord[1])))
        self.SCALE = min(scales)

        ra_space = np.linspace(self.RA_SCOPE[0], self.RA_SCOPE[1], 100)
        dec_space = np.linspace(self.DEC_SCOPE[0], self.DEC_SCOPE[1], 100)

        all_points = []
        for dec_samp in [self.DEC_SCOPE[0], self.DEC_SCOPE[1]]:
            for ra in ra_space:
                point = self.ra_dec_to_xy(ra, dec_samp)
                point = (point[0] * self.SCALE + self.CANVAS_CENTER[0], point[1] * self.SCALE + self.CANVAS_CENTER[1])
                all_points.append(point)
        for ra_samp in [self.RA_SCOPE[0], self.RA_SCOPE[1]]:
            for dec in dec_space:
                point = self.ra_dec_to_xy(ra_samp, dec)
                point = (point[0] * self.SCALE + self.CANVAS_CENTER[0], point[1] * self.SCALE + self.CANVAS_CENTER[1])
                all_points.append(point)

        arr = np.array(all_points)
        max_idx = np.argmax(arr, axis=0)
        min_idx = np.argmin(arr, axis=0)

        max_x, max_y = arr[max_idx]
        min_x, min_y = arr[min_idx]
        print(max_x, max_y)
        print(min_x, min_y)
        self.BBOX = ((min_x[0], min_y[1]), (max_x[0], max_y[1]))
        # self.chartSVG.line(min_x[0], 900, max_x[0], 1000)
        # self.chartSVG.line(900, min_y[1], 1000, max_y[1])
        # self.chartSVG.rect(min_x[0], max_y[1], max_x[0] - min_x[0], max_y[1] - min_y[1], fill="None")

    def export(self, file_name):
        self.chartSVG.export(file_name)
