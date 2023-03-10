import math
from math import sin, cos, asin, acos, sqrt
import abc
import operator
from multiprocessing import Pool

from SVG import SVG
from Body import Star, SSO
from Properties import PlotProperties as pp
import pandas as pd
import numpy as np
from astropy.coordinates import AltAz, get_body
from astropy import units as u


def polar_to_cartesian(r, theta):
    return r * cos(theta), r * sin(theta)


def ecliptic_to_equatorial(lambda_var, beta):
    epsilon = 23.439
    # https://aas.aanda.org/articles/aas/full/1998/01/ds1449/node3.html
    dec = asin(sin(beta)*cos(epsilon) + cos(beta)*sin(epsilon)*sin(lambda_var))
    ra = acos((cos(lambda_var)*cos(beta))/cos(dec))
    print(ra)
    ra2 = asin((-sin(beta)*sin(epsilon)+cos(beta)*cos(epsilon)*sin(lambda_var))/cos(dec))
    print(ra2)
    return 0, dec


# NOTE: THIS LINE NEEDS TO BE MOVED SOMEWHERE SO IT DOESN'T RUN EVERY TIME
star_df = pd.read_csv('Star CSV/hygdata_v3.csv', keep_default_na=False, nrows=100000)
master_star_list = []


def create_star(i) -> Star:
    """
    Takes index of self.star_df and creates Star() object based on column headers from main star data CSV.
    Parameters:
    ---------------
    i (int):  index of star data csv
    ---------------
    returns Star()
    """
    # Processes star information from main star dataframe (star_df) and returns Star object
    new_star = Star(star_df['ra'][i], star_df['dec'][i], star_df['mag'][i], star_df['hd'][i],
                    star_df['bayer'][i], star_df['dist'][i], star_df['proper'][i],
                    con=star_df['con'][i])
    return new_star


def gen_master_list():
    with Pool() as pool:
        result = pool.map_async(create_star, star_df.index)
        pool.close()
        pool.join()
    for star in result.get():
        master_star_list.append(star)


class Chart:
    # Note: Read this shit
    # https://www.projectpluto.com/project.htm
    def __init__(self, OBS_INFO, CANVAS_INFO):

        self.CANVAS_X, self.CANVAS_Y = CANVAS_INFO
        self.CANVAS_CENTER = (self.CANVAS_X/2, self.CANVAS_Y/2)
        self.chartSVG = SVG(self.CANVAS_X, self.CANVAS_Y,
                            background_color='black')
        self.CHART_ELEMENT_OPACITY = .25
        self.CHART_ELEMENT_WIDTH = 2.5

        self.OBS_LOC, self.OBS_TIME = OBS_INFO  # astropy EarthLocation and Time objects
        self.AA = AltAz(location=self.OBS_LOC, obstime=self.OBS_TIME)  # AltAz frame from OBS_LOC and OBS_TIME

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
        global master_star_list
        if not master_star_list:
            gen_master_list()

        self.available_stars = {}

        self.min_star_size = 1
        self.max_star_size = 8
        self.star_size_zero = 8
        self.mag_info = None
        self.sorted_stars_to_plot = []

        self.sso_list = []  # Note: probably needs a rename, something like 'active_sso_list' ?
        self.possible_sso = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']
        self.ssos_above_horizon = []

        for planet in self.possible_sso:
            self.add_sso(SSO(planet))

    # TODO: THIS SHIT BROKEN WITH NEW SYSTEM FIX IT
    @staticmethod
    def sort_stars(list_to_sort, keys, reverse_flag=False):
        """
        Sorts input list according to keys and optional reverse flag.
        Parameters:
        ---------------
        list_to_sort (list):   list of Star() objects to be sorted
        keys (list):   list of attributes of Star() to be sorted by
        reverse_flag (bool):   (optional) True indicates the list should be sorted backwards
        NOTE: As it stands, this reverse flag applies to ALL keys.
        ---------------
        returns List of sorted Star() objects
        """
        # Note: Should this be stars_above_horizon? Or all stars?
        # Note: Sorted() sucks, can't tell it which key needs to be reversed, just deal with it for now
        temp = sorted([master_star_list[i] for i in list_to_sort], key=operator.attrgetter(*keys), reverse=reverse_flag)
        sorted_indices = [master_star_list.index(x) for x in temp]  # This is probably slow as shit, not sure yet
        return sorted_indices

    def add_sso(self, sso):
        """
        Takes a SSO() object as input and preprocesses, then adds to main self.sso_list.
        Parameters:
        ---------------
        sso (SSO):   SSO() object to be added to main sso_list
        ---------------
        returns nothing
        """
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
    def plot_star(self, star):
        pass

    @abc.abstractmethod
    def plot_stars(self, num_stars, sort_filters=None, reverse_flag=False, labels=None):
        """
        Call plot_star() function given certain parameters and filters.
        Parameters:
        ---------------
        num_stars (int):   number of stars to plot
        sort_filters (list): list of filters to apply to plotting list
        reverse_flag (bool):   (optional) True indicates the list should be sorted backwards
        labels (int): number of labels to put on plot, always plots from lowest to highest magnitude
        ---------------
        returns nothing
        """
        if type(sort_filters) is not list:
            sort_filters = [sort_filters.lower()]

        self.sorted_stars_to_plot = self.sort_stars(self.available_stars.keys(), sort_filters, reverse_flag)[:num_stars]

        # Note: This can be made faster in some scenarios where sorted_stars already is sorted by mag

        sorted_stars_mag_sorted_indices = self.sort_stars(self.sorted_stars_to_plot, ['mag'])

        sorted_stars_mag_sorted = [master_star_list[i] for i in sorted_stars_mag_sorted_indices]

        sorted_stars_mag_list = [st.mag for st in sorted(sorted_stars_mag_sorted, key=lambda s: s.mag)]

        min_mag = min(sorted_stars_mag_list)
        max_mag = max(sorted_stars_mag_list)
        self.mag_info = (min_mag, max_mag)

        # Check if requested number of stars is greater than amount available to be on plot
        if num_stars > len(self.sorted_stars_to_plot):
            num_stars = len(self.sorted_stars_to_plot) - 1
            print(f"Number of stars requested is greater than available to plot, setting number to {num_stars}")
        for star_index in self.sorted_stars_to_plot:
            self.plot_star(star_index)

    def plot(self, num_stars=500, sort_filters='mag', reverse_flag=False, star_labels=None):
        # self.plot_constellations(['Ori'])
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
        # NOTE: This could all be done in a loop - would it be less readable? (?)
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
        # Note: Make this line below its own function and redo the normalization, maybe log scale? (?)
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
        self.BBOX_H = None
        self.BBOX_W = None
        self.set_scale()

        # call function to create base chart
        self.add_base_elements()

        self.find_stars_in_range()

        for star in self.available_stars:
            self.available_stars[star].x, self.available_stars[star].y = \
                self.scale_offset((self.available_stars[star].unit_x, self.available_stars[star].unit_y))

        self.min_star_size = .75
        self.max_star_size = 10

    def find_stars_in_range(self):
        for i, star in enumerate(master_star_list):
            unit_x, unit_y = self.ra_dec_to_xy(math.radians(star.ra), math.radians(star.dec))
            if self.check_in_BBOX((unit_x, unit_y)):
                new_pp = pp()
                new_pp.unit_x = unit_x
                new_pp.unit_y = unit_y
                self.available_stars[i] = new_pp

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
                point = (point[0] * self.SCALE + self.CANVAS_CENTER[0],
                         -point[1] * self.SCALE + self.CANVAS_CENTER[1])
                curve.append(point)
            self.chartSVG.curve(curve, width=2, stroke_opacity=.25, color='blue')
        if self.RA_SCOPE[1] - self.RA_SCOPE[0] != math.pi*2:
            for ra_samp in self.RA_SCOPE:
                curve = []
                for dec in dec_space:
                    point = self.ra_dec_to_xy(ra_samp, dec)
                    point = (point[0] * self.SCALE + self.CANVAS_CENTER[0],
                             -point[1] * self.SCALE + self.CANVAS_CENTER[1])
                    curve.append(point)
                self.chartSVG.curve(curve, width=2, stroke_opacity=.25, color='blue')
        if bbox:
            self.chartSVG.rect(self.BBOX[0][0], self.BBOX[1][1], self.BBOX[1][0] - self.BBOX[0][0],
                               self.BBOX[1][1] - self.BBOX[0][1], fill="None")

    def plot_star(self, star_index):
        min_mag, max_mag = self.mag_info
        # Note: max_mag - min_mag breaks if only 1 star will be displayed
        self.available_stars[star_index].size = self.max_star_size * (
                1 - (master_star_list[star_index].mag - min_mag) / (max_mag - min_mag)) + self.min_star_size

        self.chartSVG.circle(self.available_stars[star_index].x, self.available_stars[star_index].y,
                             self.available_stars[star_index].size, master_star_list[star_index].color,
                             fill="url(#StarGradient1)", width=0)

    def plot_stars(self, num_stars, sort_filters=None, reverse_flag=False, labels=None):
        super().plot_stars(num_stars, sort_filters=sort_filters, reverse_flag=reverse_flag, labels=labels)
        # if labels:
        #     for star in self.sorted_stars_to_plot[:num_stars][:labels]:
        #         self.chartSVG.text(star.x, star.y,
        #                            star.name.capitalize() if star.name else star.hd, color='blue',
        #                            dx=5 + star.size, size=15)

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

        self.unit_BBOX = ((min_x[0], min_y[1]), (max_x[0], max_y[1]))
        self.BBOX_W = (max_x[0] - min_x[0]) * self.SCALE
        self.BBOX_H = (max_y[1] - min_y[1]) * self.SCALE

        self.BBOX = (self.scale_offset((min_x[0], min_y[1])),
                     self.scale_offset((max_x[0], max_y[1])))

    def ra_dec_to_xy(self, ra, dec):
        # ra and dec input in radians
        delta_ra = ra - self.ra_center
        x = cos(dec) * math.sin(delta_ra)
        y = sin(dec) * cos(self.dec_center) - cos(dec) * cos(delta_ra) * sin(self.dec_center)

        z1 = sin(dec) * math.sin(self.dec_center) + cos(dec) * cos(self.dec_center) * cos(delta_ra)
        if not self.ORTHOGRAPHIC:
            if z1 < -.9:
                d = 20 * sqrt((1 - .81) / (1.00000001 - z1 * z1))
            else:
                d = 2 / (z1 + 1)
        else:
            d = 1
        # Note: -x because of convention of RA/Dec system and sky charts
        return -x * d, y * d

    def scale_offset(self, point):
        # input unit coordinates, tuple, (x, y)
        return point[0] * self.SCALE + self.CANVAS_CENTER[0], \
               point[1] * self.SCALE + self.CANVAS_CENTER[1]
    # + (self.CANVAS_CENTER[1] - self.BBOX_H/2)

    def check_in_BBOX(self, point):
        # input unit coordinates, tuple, (x, y)
        if self.unit_BBOX[0][0] < point[0] < self.unit_BBOX[1][0] \
                and self.unit_BBOX[0][1] < point[1] < self.unit_BBOX[1][1]:
            return True
        else:
            return False

    def export(self, file_name):
        self.chartSVG.export(file_name)
