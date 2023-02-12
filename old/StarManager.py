import math
from astropy.coordinates import AltAz
from astropy import units as u


def polar_to_cartesian(r, theta):
    return r*math.cos(theta), r*math.sin(theta)


def hms_to_deg(time):
    hour, minute, second = [int(t) for t in time.split(":")]
    return (hour * 15) + (minute * 15/60) + (second * 15/3600)


class StarManager:
    def __init__(self, MAIN_CIRCLE_INFO, OBS_INFO, chartSVG):
        self.chartSVG = chartSVG

        self.star_list = []
        self.min_mag = 0
        self.max_mag = 0
        self.stars_above_horizon = []

        self.MAIN_CIRCLE_R, self.MAIN_CIRCLE_CX, self.MAIN_CIRCLE_CY = MAIN_CIRCLE_INFO
        self.OBS_LOC, self.OBS_TIME = OBS_INFO  # astropy EarthLocation and Time objects
        self.AA = AltAz(location=self.OBS_LOC, obstime=self.OBS_TIME)
        self.min_star_size = .4
        self.max_star_size = 8.6

        self.brightest_stars_list = []

    def __repr__(self):
        self.get_mag_info()
        return f'Stars:{len(self.star_list)} | Max Mag:{self.max_mag} ' \
               f'| Min Mag: {self.min_mag}'

    def add_star(self, star):
        star_mag = star.mag
        altaz_frame = star.coord.transform_to(self.AA)
        star.az = float(altaz_frame.az.to_string(unit=u.rad, decimal=True))
        star.alt = float(altaz_frame.alt.to_string(unit=u.deg, decimal=True))
        if star.alt > 0:
            self.stars_above_horizon.append(star)
        if star_mag > self.max_mag:
            self.max_mag = star_mag
        if star_mag < self.min_mag:
            self.min_mag = star_mag
        self.star_list.append(star)

    def get_stars(self, num=None):
        if num is None:
            num = len(self.star_list)
        return self.star_list[:num]

    def plot_star(self, star):
        normalize_alt = -1 * (star.alt / 90 - 1)

        # stars with 90 should plot at center, stars with zero should be on edge, so normalize and reverse direction
        x, y = polar_to_cartesian((normalize_alt * self.MAIN_CIRCLE_R), -star.az + math.pi / 2)
        # -az because AZ increases to the east and add pi/2 to ensure north is up
        star.x, star.y = -x + self.MAIN_CIRCLE_CX, y + self.MAIN_CIRCLE_CY
        # make line below its own function
        star.rad = self.max_star_size * (1 - (star.mag - self.min_mag) / (self.max_mag - self.min_mag)) + self.min_star_size
        self.chartSVG.circle(star.x, star.y, star.rad, star.color, fill="url(#StarGradient1)", width=0)

    # TODO: add limiter so we only plot 100, 500, etc. stars\
    # TODO: add functionality to only plot subset of stars based on some filter
    def plot_stars(self, labels=False):
        for star in self.stars_above_horizon:
            self.plot_star(star)
        # get list of the brightest stars in order
        self.brightest_stars()
        if labels:
            for star in self.brightest_stars_list[:labels]:
                self.chartSVG.text(star.x, star.y, star.name.capitalize(), color="white", dx=5 + star.rad)

    def brightest_stars(self):
        self.brightest_stars_list = sorted(self.stars_above_horizon, key=lambda star: star.mag)
