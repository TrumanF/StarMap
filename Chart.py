import math
import abc
import operator
from multiprocessing import Pool

from SVG import SVG
from Body import Star, SSO

import pandas as pd
import numpy as np
from astropy.coordinates import AltAz, get_body
from astropy import units as u


def polar_to_cartesian(r, theta):
    return r * math.cos(theta), r * math.sin(theta)


# TODO: Have constellations plot before stars, will need some reworking
# Note: Add_star and add_sso are very similar, could be one function?
class Chart:
    # Note: Read this shit
    # https://www.projectpluto.com/project.htm
    def __init__(self, OBS_INFO, CANVAS_INFO):

        self.CANVAS_X, self.CANVAS_Y = CANVAS_INFO
        self.CANVAS_CENTER = (self.CANVAS_X/2, self.CANVAS_Y/2)
        self.chartSVG = SVG(self.CANVAS_X, self.CANVAS_Y,
                            background_color='black')  # NOTE: Consider making this abstract
        self.CHART_ELEMENT_OPACITY = .25
        self.CHART_ELEMENT_WIDTH = 2.5

        self.OBS_LOC, self.OBS_TIME = OBS_INFO  # astropy EarthLocation and Time objects
        self.AA = AltAz(location=self.OBS_LOC, obstime=self.OBS_TIME)  # AltAz frame from OBS_LOC and OBS_TIME

        self.star_df = pd.read_csv('Star CSV/hygdata_v3.csv', keep_default_na=False,
                                   nrows=15000)  # Note: change this magic number to some variable
        self.star_list = []
        self.cons_dict = {'Cap': [], 'Pav': [], 'CMa': [], 'Peg': [], 'Ant': [], 'Sct': [], 'Cen': [], 'Tel': [],
                          'Ori': [], 'Cae': [], 'Hyi': [], 'Mon': [], 'Ari': [], 'Cet': [], 'Lib': [], 'Dra': [],
                          'Lup': [], 'Del': [], 'Men': [], 'Oct': [], 'Aur': [], 'Lyr': [], 'Cru': [], 'Cam': [],
                          'Pyx': [], 'Eri': [], 'Tuc': [], 'Aql': [], 'Psc': [], 'CVn': [], 'Nor': [], 'Oph': [],
                          'Scl': [], 'CrA': [], 'Dor': [], 'UMa': [], 'UMi': [], 'Gru': [], 'Cha': [], 'And': [],
                          'Per': [], 'Hya': [], 'Aqr': [], 'Cir': [], 'Pic': [], 'Sex': [], 'CMi': [], 'Cyg': [],
                          'Lep': [], 'Her': [], 'Cas': [], 'Cep': [], 'Sco': [], 'Ser': [], 'Pup': [], 'Mus': [],
                          'Tri': [], 'Car': [], 'Col': [], 'Sge': [], 'Mic': [], 'LMi': [], 'Leo': [], 'Lac': [],
                          'TrA': [], 'Hor': [], 'Vul': [], 'PsA': [], 'Ara': [], 'Sgr': [], 'Phe': [], 'Aps': [],
                          'Com': [], 'CrB': [], 'Ret': [], 'Vir': [], 'Crv': [], 'Lyn': [], 'Gem': [], 'Tau': [],
                          'Vel': [], 'Crt': [], 'Boo': [], 'For': [], 'Vol': [], 'Ind': [], 'Cnc': [], 'Equ': []}

        # NOTE: Read more about pool.map_async()
        with Pool() as pool:
            result = pool.map_async(self.process_star, self.star_df.index)
            pool.close()
            pool.join()
        for star in result.get():
            self.add_star(star)

        self.min_star_size = 1
        self.max_star_size = 8
        self.star_size_zero = 8
        self.sorted_stars_to_plot = []

        self.sso_list = []  # Note: probably needs a rename, something like 'active_sso_list' ?
        self.possible_sso = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']
        self.ssos_above_horizon = []  # Note: This should exist only in RadialChart

        for planet in self.possible_sso:
            self.add_sso(SSO(planet))

    # Note: This function isn't abstract but is overriden depending on the needs of the child chart
    #  Maybe it should be?
    def add_star(self, star):
        if star.con != '':
            self.cons_dict[star.con].append(star)
        self.star_list.append(star)

    def process_star(self, i) -> Star:
        # Processes star information from main star dataframe (star_df) and returns Star object
        new_star = Star(self.star_df['ra'][i], self.star_df['dec'][i], self.star_df['mag'][i], self.star_df['hd'][i],
                        self.star_df['bayer'][i], self.star_df['dist'][i], self.star_df['proper'][i],
                        con=self.star_df['con'][i])
        return new_star

    @staticmethod
    def sort_stars(list_to_sort, keys, reverse_flag=False):
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
    def plot_star(self, star, mag_info):
        pass

    @abc.abstractmethod
    def plot_stars(self, num_stars, sort_filters=None, reverse_flag=False, labels=None):
        if type(sort_filters) is not list:
            sort_filters = [sort_filters.lower()]
        # Note: This affects the plotting size, moved [:num_stars] to for loop when plotting if want universal scale

        match self:
            case AzimuthalEQHemisphere():
                self.sorted_stars_to_plot = self.sort_stars(self.stars_above_horizon, sort_filters, reverse_flag)[:num_stars]
            case Stereographic():
                self.sorted_stars_to_plot = self.sort_stars(self.stars_in_range, sort_filters, reverse_flag)[:num_stars]
        # Note: This can be made faster in some scenarios where sorted_stars already is sorted by mag
        sorted_stars_mag_sorted = [st.mag for st in sorted(self.sorted_stars_to_plot, key=lambda s: s.mag)]
        min_mag = min(sorted_stars_mag_sorted)
        max_mag = max(sorted_stars_mag_sorted)
        # Check if requested number of stars is greater than amount available to be on plot
        if num_stars > len(self.sorted_stars_to_plot):
            num_stars = len(self.sorted_stars_to_plot) - 1
            print(f"Number of stars requested is greater than available to plot, setting number to {num_stars}")
        for star in self.sorted_stars_to_plot:
            self.plot_star(star, (min_mag, max_mag))

    def plot(self, num_stars=500, sort_filters='mag', reverse_flag=False, star_labels=None):
        self.plot_constellations(['Ori'])
        if num_stars:
            self.plot_stars(num_stars, sort_filters, reverse_flag, star_labels)

    @abc.abstractmethod
    def plot_constellations(self, constellations):
        pass


class AzimuthalEQHemisphere(Chart):
    # Uses Azimuthal equidistant projection
    def __init__(self, OBS_INFO, CANVAS_INFO):
        self.stars_above_horizon = []
        super().__init__(OBS_INFO, CANVAS_INFO)
        self.MAIN_CIRCLE_R = (self.CANVAS_Y * .9) / 2  # Note: Change multiplier to parameter
        self.SCALING_CONSTANT = self.MAIN_CIRCLE_R / 675.0  # Based on visual preference from other charts
        self.CHART_ELEMENT_WIDTH = max(1, self.SCALING_CONSTANT * self.CHART_ELEMENT_WIDTH)
        # Note: Maybe rename to CHART_CX, CY to be consistent with terminology in other charts
        self.MAIN_CIRCLE_CX = self.CANVAS_X / 2
        self.MAIN_CIRCLE_CY = self.CANVAS_Y / 2

        for star in self.stars_above_horizon:
            self.plot_preprocess_obj(star)
        # call function to create base chart
        self.add_base_elements()

    def __repr__(self):
        return f'RadialChart | Stars loaded: {len(self.star_list)} | SSOs loaded :{len(self.sso_list)}'

    def add_base_elements(self):
        self.chartSVG.circle(self.MAIN_CIRCLE_CX, self.MAIN_CIRCLE_CY, self.MAIN_CIRCLE_R, "white",
                             width=5*self.SCALING_CONSTANT, fill=False)
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

    def process_star(self, i) -> Star:
        new_star = super().process_star(i)
        star_altaz_frame = new_star.coord.transform_to(self.AA)
        new_star.az = float(star_altaz_frame.az.to_string(unit=u.rad, decimal=True))
        new_star.alt = float(star_altaz_frame.alt.to_string(unit=u.deg, decimal=True))

        return new_star

    def add_star(self, star):
        # Accepts Star object and adds to main star_list
        if star.alt > 0:
            self.stars_above_horizon.append(star)
        super().add_star(star)

    def plot_preprocess_obj(self, cel_obj):
        cel_obj.normalized_alt = -1 * (cel_obj.alt / 90 - 1)
        # stars with 90 should plot at center, stars with zero should be on edge, so normalize and reverse direction
        x, y = polar_to_cartesian((cel_obj.normalized_alt * self.MAIN_CIRCLE_R), -cel_obj.az + math.pi / 2)
        # -az because AZ increases to the east and add pi/2 to ensure north is up
        cel_obj.x, cel_obj.y = -x + self.MAIN_CIRCLE_CX, y + self.MAIN_CIRCLE_CY

    def plot(self, num_stars=500, SSOs=True, sort_filters='mag', reverse_flag=False, star_labels=None):
        super().plot(num_stars=num_stars, sort_filters=sort_filters, reverse_flag=reverse_flag,
                     star_labels=star_labels)
        if SSOs:
            self.plot_ssos(SSOs)

    def plot_star(self, star, mag_info):

        # Note: This works great, but if I wanted to plot again with different
        #  visual parameters, I'd have to re-preprocess, which doesn't need to happen since the xy
        #  coords would be the same
        #  Although, I would have to call this function every time if I changed the main circle size
        min_mag, max_mag = mag_info
        # Note: Make this line below its own function and redo the normalization, maybe log scale?
        # star.size = self.max_star_size * (
        #         1 - (star.mag - min_mag) / (max_mag - min_mag)) + self.min_star_size
        star.size = 10**(star.mag/(-10.25)) * self.star_size_zero + .25
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
        super().plot_stars(num_stars, sort_filters=sort_filters, reverse_flag=reverse_flag, labels=labels)
        if labels:
            for star in self.sorted_stars_to_plot[:num_stars][:labels]:
                self.chartSVG.text(star.x, star.y, star.name.capitalize() if star.name else star.hd, color=star.color,
                                   dx=5 + star.size, size=15*self.SCALING_CONSTANT)

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

    # TODO: Only plot constellations that are above horizon
    def plot_constellations(self, constellations):
        for constellation in constellations:
            line_pairs = []
            file = open(f"constellation lines CSV/{constellation}_lines.csv", encoding='utf-8-sig')
            for line in file.readlines():
                line_pairs.append(line.strip().split(","))
            # Note: Can be slightly more efficient by storing intermediate results
            for pair in line_pairs:
                star1 = next(star for star in self.cons_dict[constellation] if star.bayer == pair[0])
                star2 = next(star for star in self.cons_dict[constellation] if star.bayer == pair[1])
                if star1.alt > 0 and star2.alt > 2:
                    self.chartSVG.line(star1.x, star1.y, star2.x, star2.y, color='red', opacity=.75)

    def export(self, file_name):
        self.chartSVG.export(file_name)


# TODO: Add SSO support for Stereographic (?)
# Note: The constellation CSV are graphing backwards right now... Can be fixed by returning -x in ra_dec_to_xy
# TODO: BBOX should be centered, not initial plotting point
class Stereographic(Chart):
    def __init__(self, OBS_INFO, CANVAS_INFO, area, Orthographic=False):
        self.ORTHOGRAPHIC = Orthographic
        self.ra_center, self.dec_center = area.center   # rads
        self.RA_SCOPE = area.RA_SCOPE  # tuple, rads
        self.DEC_SCOPE = area.DEC_SCOPE  # tuple, rads

        if abs(self.RA_SCOPE[0] - self.RA_SCOPE[1]) > math.radians(12*15):
            print("Resetting dec_center")
            if abs(self.DEC_SCOPE[0]) < abs(self.DEC_SCOPE[1]):
                self.dec_center = math.radians(90)
            else:
                self.dec_center = math.radians(-90)

        self.RA_RANGE = area.RA_RANGE  # float, rads
        self.DEC_RANGE = area.DEC_RANGE  # float, rads

        super().__init__(OBS_INFO, CANVAS_INFO)

        self.MAX_X_SIZE = self.CANVAS_X * .8
        self.MAX_Y_SIZE = self.CANVAS_Y * .8
        self.unit_BBOX = None
        self.BBOX = None
        self.SCALE = None
        self.set_scale()

        # call function to create base chart
        self.add_base_elements()

        self.stars_in_range = []
        self.find_stars_in_range()

        for star in self.stars_in_range:
            star.x, star.y = self.scale_offset((star.unit_x, star.unit_y))

        self.min_star_size = .75
        self.max_star_size = 10

    def find_stars_in_range(self):
        for star in self.star_list:
            if self.check_in_BBOX((star.unit_x, star.unit_y)):
                self.stars_in_range.append(star)

    # TODO: Add plotting of half and quarter RA/Dec lines
    def add_base_elements(self, bbox=True):
        ra_space = np.linspace(self.RA_SCOPE[0], self.RA_SCOPE[1], 100)
        dec_space = np.linspace(self.DEC_SCOPE[0], self.DEC_SCOPE[1], 100)
        # TODO: Revisit all lines below that handle standard dec and ra lines, units need to be handled better
        all_ra_lines = np.arange(0, 24, 1)
        sample_ra_values = np.linspace(0, 24, 5000)
        all_dec_lines = np.arange(-90, 90, 10)
        sample_dec_values = np.linspace(-90, 90, 5000)

        for dec_val in all_dec_lines[1:]:
            dec_val = math.radians(dec_val)
            curve = []
            last_point_added = True
            for ra in sample_ra_values:
                ra = math.radians(ra*15)
                point = self.ra_dec_to_xy(ra, dec_val)
                if self.check_in_BBOX(point):
                    if last_point_added:
                        point = (point[0] * self.SCALE + self.CANVAS_CENTER[0],
                                 -point[1] * self.SCALE + self.CANVAS_CENTER[1])
                        curve.append(point)
                        last_point_added = True
                    else:
                        if len(curve) >= 2:
                            self.chartSVG.curve(curve, width=2, stroke_opacity=.5)
                            curve = []
                        last_point_added = True
                else:
                    last_point_added = False
            if len(curve) < 2:
                continue
            self.chartSVG.curve(curve, width=2, stroke_opacity=.5)

        for ra_val in all_ra_lines[:]:
            ra_val = math.radians(ra_val*15)
            curve = []
            last_point_added = True
            for dec in sample_dec_values:
                dec = math.radians(dec)
                point = self.ra_dec_to_xy(ra_val, dec)
                if self.check_in_BBOX(point):
                    if last_point_added:
                        point = (point[0] * self.SCALE + self.CANVAS_CENTER[0],
                                 -point[1] * self.SCALE + self.CANVAS_CENTER[1])
                        curve.append(point)
                        last_point_added = True
                    else:
                        if len(curve) >= 2:
                            self.chartSVG.curve(curve, width=2, stroke_opacity=.5)
                            curve = []
                        last_point_added = True
                else:
                    last_point_added = False
            if len(curve) < 2:
                continue
            # to get rid of the 'singularity' that happens at cos(90degrees) for ra_dec_to_xy()
            if abs(self.dec_center) == math.radians(90):
                curve = curve[1:]
            self.chartSVG.curve(curve, width=2, stroke_opacity=.5)

        # drawing area asked for
        for dec_samp in self.DEC_SCOPE:
            curve = []
            for ra in ra_space:
                point = self.ra_dec_to_xy(ra, dec_samp)
                point = (point[0] * self.SCALE + self.CANVAS_CENTER[0], -point[1] * self.SCALE + self.CANVAS_CENTER[1])
                curve.append(point)
            self.chartSVG.curve(curve, width=2, stroke_opacity=.25, color='blue')
        if self.RA_SCOPE[1] - self.RA_SCOPE[0] != math.pi*2:
            for ra_samp in self.RA_SCOPE:
                curve = []
                for dec in dec_space:
                    point = self.ra_dec_to_xy(ra_samp, dec)
                    point = (point[0] * self.SCALE + self.CANVAS_CENTER[0], -point[1] * self.SCALE + self.CANVAS_CENTER[1])
                    curve.append(point)
                self.chartSVG.curve(curve, width=2, stroke_opacity=.25, color='blue')
        if bbox:
            self.chartSVG.rect(self.BBOX[0][0], self.BBOX[1][1], self.BBOX[1][0] - self.BBOX[0][0],
                               self.BBOX[1][1] - self.BBOX[0][1], fill="None")

    def process_star(self, i) -> Star:
        new_star = super().process_star(i)
        self.plot_preprocess_obj(new_star)
        return new_star

    def plot_preprocess_obj(self, cel_obj):
        cel_obj.unit_x, cel_obj.unit_y = self.ra_dec_to_xy(math.radians(cel_obj.ra), math.radians(cel_obj.dec))

    def plot_star(self, star, mag_info):
        # self.plot_preprocess_obj(star)
        min_mag, max_mag = mag_info
        # make line below its own function?
        star.size = self.max_star_size * (
                1 - (star.mag - min_mag) / (max_mag - min_mag)) + self.min_star_size
        self.chartSVG.circle(star.x, star.y,
                             star.size, star.color, fill="url(#StarGradient1)", width=0)

    def plot_stars(self, num_stars, sort_filters=None, reverse_flag=False, labels=None):
        super().plot_stars(num_stars, sort_filters=sort_filters, reverse_flag=reverse_flag, labels=labels)
        # Note: Come back to labels
        if labels:
            for star in self.sorted_stars_to_plot[:num_stars][:labels]:
                self.chartSVG.text(star.x, star.y,
                                   star.name.capitalize() if star.name else star.hd, color=star.color,
                                   dx=5 + star.size, size=15)

    # TODO: Check if plotting will occur outside BBOX
    def plot_constellations(self, constellations):
        for constellation in constellations:
            line_pairs = []
            file = open(f"constellation lines CSV/{constellation}_lines.csv", encoding='utf-8-sig')
            for line in file.readlines():
                line_pairs.append(line.strip().split(","))
            # Note: Can be slightly more efficient by storing intermediate results
            for pair in line_pairs:
                star1 = next(star for star in self.cons_dict[constellation] if star.bayer == pair[0])
                star2 = next(star for star in self.cons_dict[constellation] if star.bayer == pair[1])
                if self.check_in_BBOX((star1.unit_x, star1.unit_y)) and self.check_in_BBOX((star2.unit_x, star2.unit_y)):
                    self.chartSVG.line(star1.x, star1.y, star2.x, star2.y, color='blue', opacity=.85)

    def set_scale(self):
        ra_space = np.linspace(self.RA_SCOPE[0], self.RA_SCOPE[1], 100)
        dec_space = np.linspace(self.DEC_SCOPE[0], self.DEC_SCOPE[1], 100)

        all_points = []
        for dec_samp in [self.DEC_SCOPE[0], self.DEC_SCOPE[1]]:
            for ra in ra_space:
                point = self.ra_dec_to_xy(ra, dec_samp)
                point = (point[0], point[1])
                all_points.append(point)
        for ra_samp in [self.RA_SCOPE[0], self.RA_SCOPE[1]]:
            for dec in dec_space:
                point = self.ra_dec_to_xy(ra_samp, dec)
                point = (point[0], point[1])
                all_points.append(point)

        np_all_points = np.array(all_points)
        max_idx = np.argmax(np_all_points, axis=0)
        min_idx = np.argmin(np_all_points, axis=0)

        max_x, max_y = np_all_points[max_idx]
        min_x, min_y = np_all_points[min_idx]

        scales = ((self.MAX_X_SIZE / (max_x[0] - min_x[0])), (self.MAX_Y_SIZE / (max_y[1] - min_y[1])))
        self.SCALE = min(scales)
        # Note: Maybe BBOX should be scaled when actually being plotted?
        self.unit_BBOX = ((min_x[0], min_y[1]), (max_x[0], max_y[1]))
        self.BBOX = (self.scale_offset((min_x[0], min_y[1])),
                     self.scale_offset((max_x[0], max_y[1])))
        print(self.BBOX)
        print(self.unit_BBOX)

    def ra_dec_to_xy(self, ra, dec):
        # ra and dec input in radians
        delta_ra = ra - self.ra_center
        x = math.cos(dec) * math.sin(delta_ra)
        y = math.sin(dec) * math.cos(self.dec_center) - math.cos(dec) * math.cos(delta_ra) * math.sin(self.dec_center)

        z1 = math.sin(dec) * math.sin(self.dec_center) + math.cos(dec) * math.cos(self.dec_center) * math.cos(delta_ra)
        if not self.ORTHOGRAPHIC:
            if z1 < -.9:
                d = 20 * math.sqrt((1 - .81) / (1.00000001 - z1 * z1))
            else:
                d = 2 / (z1 + 1)
        else:
            d = 1
        # Note: -x because of convention of RA/Dec system and sky charts
        return -x * d, y * d

    def scale_offset(self, point):
        # input unit coordinates, tuple, (x, y)
        return point[0] * self.SCALE + self.CANVAS_CENTER[0], point[1] * self.SCALE + self.CANVAS_CENTER[1]

    def check_in_BBOX(self, point):
        # input unit coordinates, tuple, (x, y)
        if self.unit_BBOX[0][0] < point[0] < self.unit_BBOX[1][0] \
                and self.unit_BBOX[0][1] < point[1] < self.unit_BBOX[1][1]:
            return True
        else:
            return False

    def export(self, file_name):
        self.chartSVG.export(file_name)
